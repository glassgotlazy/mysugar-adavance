import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --------------------------
# App Title
# --------------------------
st.set_page_config(page_title="Diabetes Tracker", layout="wide")

st.markdown(
    """
    <style>
    .top-bar {
        background-color: #4CAF50;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-size: 22px;
        color: white;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    <div class="top-bar">🩺 Diabetes Management Dashboard</div>
    """,
    unsafe_allow_html=True
)

# --------------------------
# File Upload
# --------------------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Expecting 'datetime', 'blood sugar measurement (mg/dl)', 'insulin'
        expected_cols = ['datetime', 'blood sugar measurement (mg/dl)', 'insulin']
        if not all(col in df.columns for col in expected_cols):
            st.error(f"❌ CSV must contain columns: {expected_cols}")
        else:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            df = df.sort_values(by='datetime')

            # --------------------------
            # Blood Sugar Graph
            # --------------------------
            st.subheader("📈 Blood Sugar Trends")
            fig, ax = plt.subplots()
            ax.plot(df['datetime'], df['blood sugar measurement (mg/dl)'], label="Blood Sugar", marker="o")
            ax.axhline(70, color='red', linestyle='--', label="Low (70)")
            ax.axhline(180, color='orange', linestyle='--', label="High (180)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Blood Sugar (mg/dL)")
            ax.legend()
            st.pyplot(fig)

            # --------------------------
            # Insulin Graph
            # --------------------------
            if 'insulin' in df.columns:
                st.subheader("💉 Insulin Trends")
                fig2, ax2 = plt.subplots()
                ax2.plot(df['datetime'], df['insulin'], label="Insulin (units)", color="blue", marker="s")
                ax2.set_xlabel("Date")
                ax2.set_ylabel("Insulin (units)")
                ax2.legend()
                st.pyplot(fig2)

            # --------------------------
            # Diet & Insulin Tracking
            # --------------------------
            st.subheader("🍽️ Daily Tracking")

            # Diet tracking
            diet_followed = st.checkbox("✅ Did you follow your diet today?")
            if not diet_followed:
                diet_notes = st.text_area("❌ What did you actually eat?", placeholder="Enter food details...")

            # Insulin tracking
            insulin_taken = st.checkbox("💉 Did you take your insulin as prescribed?")
            if not insulin_taken:
                insulin_notes = st.text_area("❌ What insulin adjustment did you make?", placeholder="Enter insulin changes...")

            st.success("✅ Tracking saved locally (refresh will clear input).")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("⬆️ Please upload a CSV file to continue.")
