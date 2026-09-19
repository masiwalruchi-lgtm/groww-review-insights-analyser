import os
import re
import json
import urllib.parse
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Groww Review Pulse", page_icon="📊", layout="wide")

# ------------------------------------------------------------------
# Theme legend (max 5). Keywords are regex prefixes (word start).
# ------------------------------------------------------------------
THEMES = {
    "Order Execution": {
        "icon": "⚡",
        "desc": "Trigger/SL/limit orders, price mismatch, rejected or delayed trades.",
        "kw": ["order", "trigger", "stop ?loss", r"sl\b", "execut", "slippage", "reject",
               "square ?off", "gtt", "limit", "f&o", "option", "expiry", "trade", "chart"],
        "action": "Audit SL/trigger order execution against exchange prices and show a clear rejection reason.",
    },
    "Withdrawals & Funds": {
        "icon": "💸",
        "desc": "Slow withdrawals, deposits, refunds, brokerage and charges.",
        "kw": ["withdraw", "payout", "refund", "charge", "brokerage", "fee", "fund", "money",
               "deposit", "upi", "bank", "settle", "credit", "debit", "balance", "amount",
               "transfer", "deduct"],
        "action": "Show live withdrawal status with an ETA, and make all charges visible before confirming.",
    },
    "Customer Support": {
        "icon": "🎧",
        "desc": "Slow replies, unhelpful agents, unresolved tickets.",
        "kw": ["support", "customer", "service", "agent", "ticket", "repl", "respon",
               "helpline", "complaint", "grievance", "resolv", "executive", "care"],
        "action": "Set a first-response SLA (e.g. under 24h) and auto-acknowledge every ticket with a tracking status.",
    },
    "App Stability": {
        "icon": "🛠️",
        "desc": "Crashes, lag, bugs, loading errors, device compatibility.",
        "kw": ["crash", "bug", "lag", "slow", "hang", "freez", "glitch", "error", "not working",
               "doesn'?t work", "loading", "load", "screen", "ipad", "server", "down", "update"],
        "action": "Prioritise fixes for reported device issues (iPad full screen, new iPhones) and track crash-free sessions.",
    },
    "Account & Security": {
        "icon": "🔐",
        "desc": "Login, OTP, KYC, verification, account access.",
        "kw": ["login", "log in", "sign ?in", "sign ?up", "otp", "kyc", "account", "password",
               "pin\\b", "biometric", "verif", "block", "suspend", "secur", "register",
               "onboard", "aadhaar", "pan\\b"],
        "action": "Fix login failures on new devices and add fallback login options when email or OTP fails.",
    },
}
THEME_NAMES = list(THEMES.keys())
PATTERNS = {t: re.compile(r"\b(?:" + "|".join(v["kw"]) + ")", re.I) for t, v in THEMES.items()}
UNTHEMED = "Unthemed"
MAX_WORDS = 250

STOP = set("""the a an and or but is are was were be been to of in on for with at by from this that it its
i my me we you your they them their have has had not no yes very so too can could would will just also
app groww please get got one all more when what which who how why than then there here out up down
good great nice best worst""".split())

PII_RULES = [
    (r"[\w.\-+]+@[\w.\-]+\.\w+", "[email]"),
    (r"https?://\S+|www\.\S+", "[link]"),
    (r"(?:\+?\d[\s\-]?){10,13}", "[number]"),
    (r"\b\d{6,}\b", "[id]"),
    (r"@\w+", "[handle]"),
]


def scrub(text: str) -> str:
    text = str(text)
    for pat, rep in PII_RULES:
        text = re.sub(pat, rep, text)
    return re.sub(r"\s+", " ", text).strip()


# ------------------------------------------------------------------
# LLM (optional). Set ANTHROPIC_API_KEY as env var or Streamlit secret.
# Without a key the app still works using rule-based logic.
# ------------------------------------------------------------------
def api_key():
    key = os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def llm(prompt: str, max_tokens: int = 900):
    key = api_key()
    if not key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        r = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text.strip()
    except Exception as e:  # network, quota, bad key ...
        st.session_state["llm_error"] = str(e)[:200]
        return None


def keyword_theme(text: str):
    scores = {t: len(p.findall(text)) for t, p in PATTERNS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def llm_classify(texts):
    """Classify leftover reviews with the LLM in batches. Returns {index: theme}."""
    out = {}
    for i in range(0, len(texts), 40):
        chunk = texts[i:i + 40]
        numbered = "\n".join(f"{j}: {t[:300]}" for j, t in enumerate(chunk))
        raw = llm(
            "Classify each app review into exactly one of: "
            + ", ".join(THEME_NAMES)
            + ", or None (pure praise/no specific issue).\n"
            'Return ONLY a JSON object mapping the review number to the label, e.g. {"0":"Customer Support"}.\n\n'
            + numbered,
            max_tokens=1500,
        )
        if not raw:
            continue
        try:
            data = json.loads(re.search(r"\{.*\}", raw, re.S).group())
            for k, v in data.items():
                if v in THEMES:
                    out[i + int(k)] = v
        except Exception:
            continue
    return out


@st.cache_data(show_spinner=False)
def assign_themes(df: pd.DataFrame, use_ai: bool) -> pd.DataFrame:
    df = df.copy()
    df["theme"] = df["text_all"].map(keyword_theme)
    if use_ai and api_key():
        left = df[df["theme"].isna() & (df["text"].str.len() >= 25)]
        found = llm_classify(left["text"].tolist())
        idx = left.index.tolist()
        for pos, theme in found.items():
            df.loc[idx[pos], "theme"] = theme
    df["theme"] = df["theme"].fillna(UNTHEMED)
    return df


# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
def load_data(file, weeks: int):
    if file is not None:
        raw = pd.read_csv(file)
    elif Path("data/reviews.csv").exists():
        raw = pd.read_csv("data/reviews.csv")
    else:
        return None, "No data yet. Upload a CSV in the sidebar or add data/reviews.csv."

    raw.columns = [c.strip().lower() for c in raw.columns]
    need = ["rating", "title", "text", "date"]
    if not all(c in raw.columns for c in need):
        return None, "CSV must contain: rating, title, text, date (optional: store)."

    keep = need + (["store"] if "store" in raw.columns else [])
    df = raw[keep].copy()  # drops usernames / ids / anything else
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_localize(None)
    df = df.dropna(subset=["rating", "date"])
    df["title"] = df["title"].fillna("").map(scrub)
    df["text"] = df["text"].fillna("").map(scrub)
    df["text_all"] = (df["title"] + " " + df["text"]).str.strip()
    df = df[df["text_all"].str.len() > 0]
    if df.empty:
        return None, "No usable rows after cleaning."
    cutoff = df["date"].max() - pd.Timedelta(weeks=weeks)
    df = df[df["date"] >= cutoff].reset_index(drop=True)
    return df, None


def theme_stats(df: pd.DataFrame) -> pd.DataFrame:
    t = (
        df[df["theme"] != UNTHEMED]
        .groupby("theme")
        .agg(reviews=("rating", "size"), avg=("rating", "mean"))
        .reindex(THEME_NAMES)
        .fillna(0)
    )
    sev = t["reviews"] * (5.5 - t["avg"].where(t["avg"] > 0, 5.5))
    t["priority"] = (100 * sev / sev.max()).round() if sev.max() > 0 else 0
    return t.sort_values("priority", ascending=False)


def pick_quote(df, theme, used, max_len=160):
    c = df[(df["theme"] == theme) & df["text"].str.len().between(40, max_len)]
    c = c.sort_values(["rating", "date"], ascending=[True, False])
    for _, r in c.iterrows():
        if r["text"] not in used:
            used.add(r["text"])
            return f'"{r["text"]}" ({theme}, {int(r["rating"])}★)'
    return None


def word_count(text: str) -> int:
    return len(text.split())


def build_note(df, stats):
    top = stats[stats["reviews"] > 0].head(3)
    names = top.index.tolist()
    start, end = df["date"].min().date(), df["date"].max().date()
    for max_len in (160, 140, 120, 100, 80, 60):
        used = set()
        quotes = [q for q in (pick_quote(df, t, used, max_len) for t in names) if q]
        lines = [
            "WEEKLY REVIEW PULSE - GROWW",
            f"{start} to {end} | {len(df)} reviews | avg {df['rating'].mean():.2f}/5",
            "",
            "TOP 3 THEMES",
        ]
        for i, t in enumerate(names, 1):
            lines.append(f"{i}. {t}: {int(top.loc[t, 'reviews'])} reviews, ~{top.loc[t, 'avg']:.1f}/5")
        lines += ["", "USER QUOTES"] + [f"{i}. {q}" for i, q in enumerate(quotes, 1)]
        lines += ["", "ACTION IDEAS"] + [f"{i}. {THEMES[t]['action']}" for i, t in enumerate(names, 1)]
        note = "\n".join(lines)
        if word_count(note) <= MAX_WORDS:
            break
    return note


def build_note_ai(df, stats):
    top = stats[stats["reviews"] > 0].head(3)
    used = set()
    cands = [q for t in top.index for q in [pick_quote(df, t, used, 140)] if q]
    prompt = (
        f"Write a one-page weekly app review note for Groww, {MAX_WORDS} words or fewer, plain text, scannable, neutral tone.\n"
        "Sections: TOP 3 THEMES (with review counts), USER QUOTES (3, verbatim from the list, no PII), ACTION IDEAS (3).\n\n"
        f"Window: {df['date'].min().date()} to {df['date'].max().date()}, {len(df)} reviews.\n"
        f"Theme stats:\n{top.round(2).to_string()}\n\nCandidate quotes:\n" + "\n".join(cands)
    )
    note = llm(prompt)
    return note if note and word_count(note) <= MAX_WORDS else None


def build_email(note, tone, df):
    end = df["date"].max().date()
    subject = f"Weekly Review Pulse - Groww - week ending {end}"
    if tone == "Formal":
        body = ("Hello team,\n\nPlease find this week's app review summary below.\n\n"
                f"{note}\n\nKindly review and share any follow-up actions.\n\nRegards,\nProduct Insights")
    else:
        body = ("Hey team,\n\nHere's this week's review pulse - quick read, top things users are telling us.\n\n"
                f"{note}\n\nLet's pick the top fix this week. Thoughts?\n\nCheers")
    return subject, body


def explain_theme(df, theme, stats):
    sub = df[df["theme"] == theme]
    ai = llm(
        f"In 3 short sentences, explain what users complain about in the '{theme}' theme and the most likely root cause. "
        "No PII.\nReviews:\n" + "\n".join(f"- ({int(r)}★) {t[:200]}" for r, t in zip(sub["rating"].head(40), sub["text"].head(40)))
    )
    if ai:
        return ai
    words = Counter(w for t in sub["text"] for w in re.findall(r"[a-z']{4,}", t.lower()) if w not in STOP)
    common = ", ".join(w for w, _ in words.most_common(6))
    low = int((sub["rating"] <= 2).sum())
    return (f"{len(sub)} reviews mention {theme} (avg {sub['rating'].mean():.1f}/5); {low} are 1-2 stars. "
            f"Most repeated words: {common}. Add an API key for an AI-written explanation.")


# ------------------------------------------------------------------
# Styling
# ------------------------------------------------------------------
st.markdown("""
<style>
.block-container {max-width: 1300px; padding-top: 1.5rem;}
.hero h1 {font-size: 2.4rem; font-weight: 800; margin: 0;}
.hero p {color: #475569; margin-top: .3rem;}
.g {color: #10b981;} .b {color: #2563eb;}
.kpi {background: linear-gradient(135deg,#f8fbff,#f3fff9); border: 1px solid #dbeafe;
      border-radius: 16px; padding: 1rem 1.2rem;}
.kpi .n {font-size: 1.9rem; font-weight: 800;} .kpi .l {color: #64748b; font-size: .85rem;}
.note {white-space: pre-wrap; background: #fffdf7; border: 1px solid #e7e0c8; border-radius: 14px;
       padding: 1.2rem; color: #1f2937; font-family: Georgia, serif; line-height: 1.6;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🟢 Groww")
    st.caption("Weekly Review Pulse")
    file = st.file_uploader("Upload reviews CSV", type=["csv"], help="Columns: rating, title, text, date, store (optional)")
    weeks = st.slider("Weeks of reviews", 4, 12, 12)
    has_key = bool(api_key())
    use_ai = st.toggle("Use AI (Claude)", value=has_key, disabled=not has_key)
    st.caption("🤖 AI on" if (has_key and use_ai) else "⚙️ Rule-based mode (no API key set)")
    st.info("Public reviews only. Usernames, emails, phone numbers and IDs are stripped automatically.")

st.markdown(
    '<div class="hero"><h1>Weekly Review <span class="b">Pulse</span> '
    '<span class="g">for Groww</span></h1>'
    "<p>App Store and Play Store reviews, grouped into five themes, ready to act on.</p></div>",
    unsafe_allow_html=True,
)

df, err = load_data(file, weeks)
if err:
    st.info(err)
    st.stop()

df = assign_themes(df, use_ai and has_key)
stats = theme_stats(df)
themed = int((df["theme"] != UNTHEMED).sum())
span_days = (df["date"].max() - df["date"].min()).days
if span_days < 56:
    st.warning(f"Data covers only {span_days} days. The assignment asks for 8-12 weeks, so export older reviews too.")
if st.session_state.get("llm_error"):
    st.warning(f"AI call failed, using rule-based fallback: {st.session_state['llm_error']}")

tab_over, tab_theme, tab_note, tab_mail, tab_help = st.tabs(
    ["📊 Overview", "🧩 Themes", "📝 Weekly Note", "✉️ Email Draft", "📘 README & Data"]
)

# ---------------- Overview ----------------
with tab_over:
    k = st.columns(4)
    kpis = [
        (len(df), "Reviews in window"),
        (f"{df['rating'].mean():.2f}/5", "Average rating"),
        (f"{themed} ({themed / len(df):.0%})", "Reviews placed in a theme"),
        (f"{df['date'].min().date()} to {df['date'].max().date()}", "Window"),
    ]
    for col, (n, l) in zip(k, kpis):
        col.markdown(f'<div class="kpi"><div class="n">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.write("")
    a, b = st.columns(2)
    with a:
        st.subheader("Rating distribution")
        st.bar_chart(df["rating"].round().astype(int).value_counts().reindex([1, 2, 3, 4, 5], fill_value=0))
    with b:
        st.subheader("Reviews by theme")
        st.bar_chart(stats["reviews"])
    if "store" in df.columns:
        st.subheader("Store split")
        st.bar_chart(df["store"].value_counts())
    st.caption(f"{len(df) - themed} reviews are short praise with no specific issue and sit outside the five themes.")

# ---------------- Themes ----------------
with tab_theme:
    st.caption("Tap a theme to see its reviews and ask for an explanation.")
    if "sel" not in st.session_state:
        st.session_state.sel = stats.index[0]
    cols = st.columns(len(THEME_NAMES))
    for col, (name, row) in zip(cols, stats.iterrows()):
        with col.container(border=True):
            st.markdown(f"*{THEMES[name]['icon']} {name}*")
            st.caption(f"{int(row['reviews'])} reviews | ~{row['avg']:.1f}/5")
            st.progress(int(row["priority"]) / 100, text=f"Priority {int(row['priority'])}")
            if st.button("Open", key=f"open_{name}"):
                st.session_state.sel = name
    sel = st.session_state.sel
    st.subheader(f"{THEMES[sel]['icon']} {sel}")
    st.caption(THEMES[sel]["desc"])
    if st.button("Explain this theme", key="explain"):
        with st.spinner("Reading the reviews..."):
            st.session_state["explain_text"] = (sel, explain_theme(df, sel, stats))
    ex = st.session_state.get("explain_text")
    if ex and ex[0] == sel:
        st.success(ex[1])
    view = df[df["theme"] == sel].sort_values("rating")[["rating", "text", "date"]]
    st.dataframe(view, hide_index=True)

# ---------------- Weekly note ----------------
with tab_note:
    if st.button("Generate weekly note", key="gen_note"):
        note = build_note_ai(df, stats) if (use_ai and has_key) else None
        st.session_state["note"] = note or build_note(df, stats)
    note = st.session_state.get("note")
    if note:
        n = word_count(note)
        (st.success if n <= MAX_WORDS else st.error)(f"{n} / {MAX_WORDS} words")
        st.markdown(f'<div class="note">{note}</div>', unsafe_allow_html=True)
        st.write("")
        st.download_button("Download .md", note, "weekly_note.md", "text/markdown")
    else:
        st.info("Press Generate to create the one-page note.")

# ---------------- Email ----------------
with tab_mail:
    tone = st.radio("Tone", ["Formal", "Casual"], horizontal=True)
    if st.button("Generate / regenerate email", key="gen_mail"):
        if not st.session_state.get("note"):
            st.session_state["note"] = build_note(df, stats)
        st.session_state["email"] = build_email(st.session_state["note"], tone, df)
    em = st.session_state.get("email")
    if em:
        subject, body = em
        st.text_input("Subject", subject, key="subj_view")
        st.text_area("Body", body, height=380, key="body_view")
        link = "mailto:?subject=" + urllib.parse.quote(subject) + "&body=" + urllib.parse.quote(body[:1500])
        c1, c2 = st.columns(2)
        c1.link_button("Open in mail app", link)
        c2.download_button("Download .txt", f"Subject: {subject}\n\n{body}", "email_draft.txt")
        st.caption("Send it to yourself or an alias. No PII in the body.")
    else:
        st.info("Choose a tone and press Generate.")

# ---------------- README & data ----------------
with tab_help:
    st.subheader("How to re-run for a new week")
    st.markdown(
        "1. Export fresh public reviews to a CSV (rating, title, text, date, store).\n"
        "2. Upload it in the sidebar, or replace data/reviews.csv.\n"
        "3. Pick 8-12 weeks, then press *Generate weekly note* and *Generate email*."
    )
    st.subheader("Theme legend")
    for name, v in THEMES.items():
        st.markdown(f"- {v['icon']} *{name}*: {v['desc']}")
    st.download_button("Download cleaned reviews CSV", df[["rating", "title", "text", "date"] + (["store"] if "store" in df.columns else [])].to_csv(index=False),
                       "reviews_clean.csv", "text/csv")

st.caption("Public app-review data only. No usernames, emails or IDs are stored or shown.")
