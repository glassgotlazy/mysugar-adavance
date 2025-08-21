import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# Flexible column mappings
COLUMN_ALIASES = {
    "datetime": ["datetime", "date", "time", "timestamp", "date/time", "date time"],
    "blood sugar measurement (mg/dl)": [
        "blood sugar measurement (mg/dl)", "blood sugar", "glucose",
        "blood sugar measurement", "sugar level", "bs"
    ],
    "insulin": ["insulin", "insulin dose", "insulin units", "insulin taken"]
}

def normalize_columns(df):
    col_map = {}
    for standard, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if col.strip().lower() in [a.lower() for a in aliases]:
                col_map[col] = standard
                break
    df = df.rename(columns=col_map)
    return df

# Streamlit UI
st.set_page_config(page_title="MySugar Advance", layout="wide")

st.title("📊 MySugar Advance - Blood Sugar & Insulin Tracker")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df = normalize_columns(df)

        required_cols = ["datetime", "blood sugar measurement (mg/dl)", "insulin"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ CSV must contain columns: {required_cols}")
        else:
            # Convert datetime
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df = df.dropna(subset=["datetime"])
            df = df.sort_values("datetime")

            st.success("✅ File uploaded and processed successfully!")

            # Show table with checkboxes for diet & insulin tracking
            st.subheader("📋 Daily Tracking")
            df["Diet Followed?"] = st.checkbox("Tick if diet was followed", value=True)
            df["Diet Notes"] = ""
            df["Insulin Taken?"] = st.checkbox("Tick if insulin was taken", value=True)
            df["Insulin Notes"] = ""

            st.dataframe(df)

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
