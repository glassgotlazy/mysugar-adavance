import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# List of possible insulin-related columns
INSULIN_COLS = [
    "insulin injection units (pen)",
    "basal injection units",
    "insulin injection units (pump)",
    "insulin (meal)",
    "insulin (correction)"
]

st.set_page_config(page_title="MySugar Advance", layout="wide")

st.title("📊 MySugar Advance - Blood Sugar & Insulin Tracker")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Normalize column names (lowercase for matching)
        df.columns = [col.strip().lower() for col in df.columns]

        # Fix duplicate datetime column issue (take first one)
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]

        # Ensure datetime column
        if "datetime" not in df.columns:
            st.error("❌ No 'datetime' column found.")
        elif "blood sugar measurement (mg/dl)" not in df.columns:
            st.error("❌ No 'blood sugar measurement (mg/dl)' column found.")
        else:
            # Combine all insulin columns into one
            df["insulin"] = 0
            for col in INSULIN_COLS:
                if col in df.columns:
                    df["insulin"] += pd.to_numeric(df[col], errors="coerce").fillna(0)

            # Convert datetime safely
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df = df.dropna(subset=["datetime"])
            df = df.sort_values("datetime")

            st.success("✅ File uploaded and processed successfully!")

            # Show data preview
            st.subheader("📋 Uploaded Data")
            st.dataframe(df[["datetime", "blood sugar measurement (mg/dl)", "insulin"]].head())

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
            st.subheader("💉 Insulin Trend (Sum of All Types)")
            fig2, ax2 = plt.subplots()
            ax2.bar(df["datetime"], df["insulin"], color="blue", label="Insulin")
            ax2.set_ylabel("Insulin Units")
            ax2.set_xlabel("Date/Time")
            ax2.legend()
            st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
