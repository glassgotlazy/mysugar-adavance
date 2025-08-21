import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# Define required columns
REQUIRED_COLS = {
    "datetime": ["datetime", "date", "time", "timestamp", "date/time", "date time"],
    "blood sugar measurement (mg/dl)": [
        "blood sugar measurement (mg/dl)", "blood sugar", "glucose",
        "blood sugar measurement", "sugar level", "bs", "bg"
    ],
    "insulin": ["insulin", "insulin dose", "insulin units", "insulin taken"]
}

def normalize_columns(df):
    col_map = {}
    for standard, aliases in REQUIRED_COLS.items():
        for col in df.columns:
            clean_col = re.sub(r"[^a-z0-9]", "", col.strip().lower())
            for alias in aliases:
                if clean_col == re.sub(r"[^a-z0-9]", "", alias.lower()):
                    col_map[col] = standard
                    break
    return df.rename(columns=col_map)

# Streamlit UI
st.set_page_config(page_title="MySugar Advance", layout="wide")

st.title("📊 MySugar Advance - Blood Sugar & Insulin Tracker")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = normalize_columns(df)

        # Validate columns
        if not all(col in df.columns for col in REQUIRED_COLS.keys()):
            st.error(f"❌ CSV must contain columns (any case/format accepted): {list(REQUIRED_COLS.keys())}")
            st.write("📌 Detected columns in your file:", list(df.columns))
        else:
            # Convert datetime safely
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df = df.dropna(subset=["datetime"])
            df = df.sort_values("datetime")

            st.success("✅ File uploaded and processed successfully!")

            # Show data preview
            st.subheader("📋 Uploaded Data")
            st.dataframe(df.head())

            # Plot Blood Sugar
            st.subheader("📈 Blood Sugar Trend")
            fig, ax = plt.subplots()
            ax.plot(df["datetime"], df["blood sugar measurement (mg/dl)"], marker="o", label="Blood Sugar")
            ax.axhline(70, color="red", linestyle="--", label="Low Threshold (70)")
            ax.axhline(140, color="green", linestyle="--", label="High Threshold (140)")
            ax.set_ylabel("Blood Sugar (mg/dL)")
            ax.set_xlabel("Date/Time")
            ax.legend()
            st.pyplot(fig)

            # Plot Insulin
            st.subheader("💉 Insulin Trend")
            fig2, ax2 = plt.subplots()
            ax2.bar(df["datetime"], df["insulin"], color="blue", label="Insulin")
            ax2.set_ylabel("Insulin Units")
            ax2.set_xlabel("Date/Time")
            ax2.legend()
            st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
