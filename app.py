import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# --- App title ---
st.set_page_config(page_title="MySugar Advance", layout="wide")
st.title("📊 MySugar Advance - Blood Sugar & Insulin Tracker")

# --- File uploader ---
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    # Load and clean CSV
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Check required columns
    if "date" in df.columns and "time" in df.columns:
        df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str), errors="coerce")
    else:
        st.error("❌ CSV must have both 'date' and 'time' columns")
        st.stop()

    if "blood sugar measurement (mg/dl)" not in df.columns:
        st.error("❌ CSV missing 'blood sugar measurement (mg/dl)' column")
        st.stop()

    # Merge insulin columns into one
    insulin_cols = [
        "insulin injection units (pen)",
        "basal injection units",
        "insulin injection units (pump)",
        "insulin (meal)",
        "insulin (correction)"
    ]
    df["insulin"] = df[insulin_cols].fillna(0).sum(axis=1)

    # Keep only required
    df = df[["datetime", "blood sugar measurement (mg/dl)", "insulin"]].dropna()

    st.success("✅ File processed successfully!")

    # --- Compliance Log ---
    log_file = "compliance_log.csv"
    if not os.path.exists(log_file):
        pd.DataFrame(columns=["datetime", "blood_sugar", "insulin", "diet_followed", "diet_notes", "insulin_taken", "insulin_notes"]).to_csv(log_file, index=False)

    st.subheader("📝 Daily Compliance Log")

    for i, row in df.iterrows():
        with st.expander(f"📌 {row['datetime']} | Sugar: {row['blood sugar measurement (mg/dl)']} mg/dL | Insulin: {row['insulin']} units"):
            diet_followed = st.checkbox(f"✅ Diet followed? (Row {i})", value=True, key=f"diet_{i}")
            diet_notes = ""
            if not diet_followed:
                diet_notes = st.text_input(f"❌ What was eaten instead? (Row {i})", key=f"diet_notes_{i}")

            insulin_taken = st.checkbox(f"💉 Insulin taken? (Row {i})", value=True, key=f"insulin_{i}")
            insulin_notes = ""
            if not insulin_taken:
                insulin_notes = st.text_input(f"❌ What was done instead of insulin? (Row {i})", key=f"insulin_notes_{i}")

            if st.button(f"💾 Save Log for Row {i}", key=f"save_{i}"):
                new_entry = {
                    "datetime": row["datetime"],
                    "blood_sugar": row["blood sugar measurement (mg/dl)"],
                    "insulin": row["insulin"],
                    "diet_followed": diet_followed,
                    "diet_notes": diet_notes,
                    "insulin_taken": insulin_taken,
                    "insulin_notes": insulin_notes
                }
                log_df = pd.read_csv(log_file)
                log_df = pd.concat([log_df, pd.DataFrame([new_entry])], ignore_index=True)
                log_df.to_csv(log_file, index=False)
                st.success(f"✅ Saved compliance log for {row['datetime']}")

    # --- Graphs ---
    st.subheader("📈 Trends")

    fig1, ax1 = plt.subplots()
    ax1.plot(df["datetime"], df["blood sugar measurement (mg/dl)"], marker="o", label="Blood Sugar (mg/dL)")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Blood Sugar (mg/dL)")
    ax1.legend()
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(df["datetime"], df["insulin"], marker="s", color="orange", label="Insulin (units)")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Insulin (units)")
    ax2.legend()
    st.pyplot(fig2)

else:
    st.info("⬆️ Please upload a CSV file to get started.")
