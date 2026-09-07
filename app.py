import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Groww Review Insights Analyser",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

.hero {
    padding: 1.3rem 0 0.8rem 0;
}

.hero-small {
    letter-spacing: 0.25rem;
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 600;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 0.5rem;
    margin-bottom: 0.7rem;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #475569;
    max-width: 1000px;
}

.feature-card {
    background: #f8fbff;
    border: 1px solid #e6edf5;
    border-radius: 18px;
    padding: 1rem;
    min-height: 120px;
}

.feature-icon {
    font-size: 1.8rem;
}

.feature-title {
    font-weight: 700;
    margin-top: 0.4rem;
}

.feature-text {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 0.2rem;
}

.upload-box {
    background: linear-gradient(135deg, #f8fbff 0%, #f5fff9 100%);
    border: 1px solid #dbeafe;
    border-radius: 22px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.info-card {
    background: #ffffff;
    border: 1px solid #e6edf5;
    border-radius: 18px;
    padding: 1rem;
    min-height: 125px;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.quote-box {
    background: linear-gradient(90deg, #f0fdf4, #eff6ff);
    border-radius: 18px;
    padding: 1.2rem;
    border: 1px solid #dcfce7;
}

.small-muted {
    color: #64748b;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("## 🟢 Groww")
    st.caption("Review Insights Analyser")

    st.markdown("---")

    st.markdown("### Navigation")
    st.write("🏠 Home")
    st.write("📊 Review Analysis")
    st.write("🧠 Weekly Pulse")
    st.write("✉️ Email Draft")
    st.write("🔒 Privacy")

    st.markdown("---")

    st.info(
        "Use only public app reviews. "
        "Do not upload usernames, emails, phone numbers or IDs."
    )

# -----------------------------
# Hero
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-small">LISTEN • ANALYSE • IMPROVE</div>
    <div class="hero-title">
        Groww App Review <span style="color:#2563eb;">Insights</span>
        <span style="color:#10b981;">Analyser</span>
    </div>
    <div class="hero-subtitle">
        Turn recent app-store reviews into clear, actionable weekly insights
        for Product, Growth and Support teams.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Feature Cards
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔎</div>
        <div class="feature-title">Find what users feel</div>
        <div class="feature-text">Identify positive and negative feedback quickly.</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-title">Discover key themes</div>
        <div class="feature-text">Group reviews into a maximum of five themes.</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💬</div>
        <div class="feature-title">Select real quotes</div>
        <div class="feature-text">Surface representative user feedback without PII.</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Create action ideas</div>
        <div class="feature-text">Turn recurring pain points into product actions.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Upload Reviews CSV</div>',
    unsafe_allow_html=True
)

left, right = st.columns([1.35, 1])

with left:
    uploaded_file = st.file_uploader(
        "Upload your review dataset",
        type=["csv"],
        help="Required columns: rating, title, text, date"
    )
    st.caption("Accepted format: CSV")

with right:
    st.markdown("### 📄 Expected CSV Format")

    sample_df = pd.DataFrame({
        "rating": [5, 1, 4],
        "title": ["", "", ""],
        "text": [
            "Very useful app",
            "Customer support is slow",
            "Easy to use"
        ],
        "date": [
            "2026-09-01",
            "2026-08-31",
            "2026-08-30"
        ]
    })

    st.dataframe(
        sample_df,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "Privacy rule: do not include usernames, emails, IDs "
        "or other personally identifiable information."
    )

st.markdown(
    '<div class="section-title">Why this helps product teams</div>',
    unsafe_allow_html=True
)

b1, b2, b3, b4 = st.columns(4)

with b1:
    st.markdown("""
    <div class="info-card">
        <h4>👥 Understand sentiment</h4>
        <div class="small-muted">See what matters most to users.</div>
    </div>
    """, unsafe_allow_html=True)

with b2:
    st.markdown("""
    <div class="info-card">
        <h4>⚙️ Prioritise fixes</h4>
        <div class="small-muted">Spot recurring pain points worth solving.</div>
    </div>
    """, unsafe_allow_html=True)

with b3:
    st.markdown("""
    <div class="info-card">
        <h4>⏱️ Save time</h4>
        <div class="small-muted">Analyse hundreds of reviews faster.</div>
    </div>
    """, unsafe_allow_html=True)

with b4:
    st.markdown("""
    <div class="info-card">
        <h4>❤️ Build better products</h4>
        <div class="small-muted">Turn feedback into clear product actions.</div>
    </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_columns = ["rating", "title", "text", "date"]

    if all(col in df.columns for col in required_columns):

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        st.success("✅ Reviews uploaded successfully!")

        st.markdown(
            '<div class="section-title">Dataset Overview</div>',
            unsafe_allow_html=True
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Reviews", len(df))

        with m2:
            st.metric(
                "Average Rating",
                round(df["rating"].mean(), 2)
            )

        with m3:
            st.metric(
                "Newest Review",
                df["date"].max().date()
                if not df["date"].isna().all()
                else "N/A"
            )

        with m4:
            st.metric(
                "Oldest Review",
                df["date"].min().date()
                if not df["date"].isna().all()
                else "N/A"
            )

        st.markdown(
            '<div class="section-title">Review Preview</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            df[["rating", "title", "text", "date"]].head(20),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(
            '<div class="section-title">AI Review Analysis</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="quote-box">
            The AI workflow will identify the most important review themes,
            select real user quotes and suggest actionable product ideas.
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button(
            "✨ Analyse Reviews",
            use_container_width=True
        ):
            st.info(
                "The interface is ready. "
                "We will connect the LLM analysis in the next step."
            )

    else:
        st.error(
            "Your CSV must contain these columns: "
            "rating, title, text, date"
        )

st.markdown("---")

st.caption(
    "Built for learning and product-thinking purposes • "
    "Public app-review data only"
)
