import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

        # Normalize column names (lowercase, strip spaces)
        df.columns = [col.strip().lower() for col in df.columns]

        # If there are duplicate datetime columns, keep the first one
        if "datetime" in df.columns:
            datetime_cols = [c for c in df.columns if c == "datetime"]
            if len(datetime_cols) > 1:
                # rename extra ones
                for i, col in enumerate(datetime_cols[1:], start=2):
                    df.rename(columns={col: f"datetime_{i}"}, inplace=True)

        # Check mandatory columns
        if "datetime" not in df.columns:
            st.error("❌ No 'datetime' column found in file after cleaning.")
        elif "blood sugar measurement (mg/dl)" not in df.columns:
            st.error("❌ No 'blood sugar measurement (mg/dl)' column found.")
        else:
            # Convert datetime safely
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df = df.dropna(subset=["datetime"])
            df = df.sort_values("datetime")

            # Ensure insulin columns are numeric
            for col in INSULIN_COLS.keys():
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            st.success("✅ File uploaded and processed successfully!")

            # Show Data Preview
            preview_cols = ["datetime", "blood sugar measurement (mg/dl)"] + [
                col for col in INSULIN_COLS.keys() if col in df.columns
            ]
            st.subheader("📋 Uploaded Data")
            st.dataframe(df[preview_cols].head())

            # Blood Sugar Trend
            st.subheader("📈 Blood Sugar Trend")
            fig, ax = plt.subplots()
            ax.plot(df["datetime"], df["blood sugar measurement (mg/dl)"], marker="o", label="Blood Sugar")
            ax.axhline(70, color="red", linestyle="--", label="Low Threshold (70)")
            ax.axhline(140, color="green", linestyle="--", label="High Threshold (140)")
            ax.set_ylabel("Blood Sugar (mg/dL)")
            ax.set_xlabel("Date/Time")
            ax.legend()
            st.pyplot(fig)

            # Insulin Trends - Separated by Type
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
