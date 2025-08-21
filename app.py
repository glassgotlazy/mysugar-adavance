import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# Define insulin-related columns
INSULIN_COLS = {
    "insulin injection units (pen)": "Pen",
    "basal injection units": "Basal",
    "insulin injection units (pump)": "Pump",
    "insulin (meal)": "Meal",
    "insulin (correction)": "Correction"
}

st.set_page_config(page_title="MySugar Advance", layout="wide")
st.title("📊 MySugar Advance - Blood Sugar & Insulin Tracker")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Clean column names
        df.columns = [re.sub(r"[^a-z0-9 ()/_-]", "", col.lower().strip()) for col in df.columns]
        st.write("📌 Cleaned columns:", list(df.columns))

        # If we have date + time, combine into datetime
        if "date" in df.columns and "time" in df.columns:
            df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str), errors="coerce")
        elif "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        else:
            st.error("❌ No 'date' + 'time' or 'datetime' column found.")
            st.stop()

        # Blood sugar column
        sugar_candidates = [c for c in df.columns if "blood sugar" in c]
        if not sugar_candidates:
            st.error("❌ No 'blood sugar measurement (mg/dl)' column found.")
            st.stop()
        sugar_col = sugar_candidates[0]

        # Drop rows without datetime
        df = df.dropna(subset=["datetime"])
        df = df.sort_values("datetime")

        # Ensure insulin columns are numeric
        for col in INSULIN_COLS.keys():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        st.success("✅ File uploaded and processed successfully!")

        # Show Data Preview
        preview_cols = ["datetime", sugar_col] + [col for col in INSULIN_COLS.keys() if col in df.columns]
        st.subheader("📋 Uploaded Data")
        st.dataframe(df[preview_cols].head())

        # Blood Sugar Trend
        st.subheader("📈 Blood Sugar Trend")
        fig, ax = plt.subplots()
        ax.plot(df["datetime"], df[sugar_col], marker="o", label="Blood Sugar")
        ax.axhline(70, color="red", linestyle="--", label="Low Threshold (70)")
        ax.axhline(140, color="green", linestyle="--", label="High Threshold (140)")
        ax.set_ylabel("Blood Sugar (mg/dL)")
        ax.set_xlabel("Date/Time")
        ax.legend()
        st.pyplot(fig)

        # Insulin Trends
        st.subheader("💉 Insulin Trends by Type")
        for col, label in INSULIN_COLS.items():
            if col in df.columns:
                st.markdown(f"**{label} Insulin**")
                fig2, ax2 = plt.subplots()
                ax2.bar(df["datetime"], df[col], color="blue", label=f"{label} Insulin")
                ax2.set_ylabel("Units")
                ax2.set_xlabel("Date/Time")
                ax2.legend()
                st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
