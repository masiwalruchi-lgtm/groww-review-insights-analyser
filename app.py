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
   …
