import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Groww Review Insights Analyser",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Groww App Review Insights Analyser")

st.write(
    "Turn recent app-store reviews into a weekly product pulse "
    "for Product, Growth and Support teams."
)

st.info(
    "Upload a CSV containing public app reviews. "
    "No usernames, emails or user IDs should be included."
)

uploaded_file = st.file_uploader(
    "Upload Reviews CSV",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    required_columns = ["rating", "title", "text", "date"]

    if all(column in df.columns for column in required_columns):

        st.success("✅ Reviews uploaded successfully!")

        # Convert date column
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Basic metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Reviews", len(df))

        with col2:
            st.metric(
                "Average Rating",
                round(df["rating"].mean(), 2)
            )

        with col3:
            st.metric(
                "Date Range",
                f"{df['date'].min().date()} → {df['date'].max().date()}"
            )

        st.subheader("Review Preview")

        st.dataframe(
            df[["rating", "title", "text", "date"]].head(20),
            use_container_width=True
        )

        st.divider()

        st.subheader("🤖 AI Review Analysis")

        st.write(
            "The next step will group these reviews into themes, "
            "identify representative user quotes and generate "
            "product action ideas."
        )

        if st.button("Analyse Reviews"):
            st.info("AI analysis will be connected in the next step.")

    else:

        st.error(
            "CSV must contain these columns: "
            "rating, title, text, date"
        )

else:
    st.caption("Upload your Groww reviews CSV to begin.")
