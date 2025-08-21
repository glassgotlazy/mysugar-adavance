import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io

# ----------------------------
# App title and layout
# ----------------------------
st.set_page_config(page_title="Diabetes Tracker", layout="wide")

st.markdown(
    """
    <style>
    .top-bar {
        background-color: #4CAF50;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    <div class="top-bar">📊 Diabetes Tracker</div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# File upload
# ----------------------------
uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read CSV
        df = pd.read_csv(uploaded_file)

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Rename common variants
        df.rename(
            columns={
                "date": "datetime",
                "time": "datetime",
                "blood sugar": "blood sugar measurement (mg/dl)",
                "blood sugar level": "blood sugar measurement (mg/dl)",
                "glucose": "blood sugar measurement (mg/dl)",
                "insulin dose": "insulin",
            },
            inplace=True,
        )

        # Required columns
        required_cols = ["datetime", "blood sugar measurement (mg/dl)", "insulin"]

        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ CSV must contain columns: {required_cols}")
        else:
            # Convert datetime
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df.dropna(subset=["datetime"], inplace=True)

            # Sort by time
            df.sort_values("datetime", inplace=True)

            st.success("✅ File uploaded and processed successfully!")

            # ----------------------------
            # Display data
            # ----------------------------
            st.subheader("📋 Uploaded Data Preview")
            st.dataframe(df.head())

            # ----------------------------
            # Diet & Insulin Tracking
            # ----------------------------
            st.subheader("🍽️ Diet & 💉 Insulin Tracking")

            diet_followed = st.checkbox("✅ Did you follow your diet plan?")
            diet_notes = ""
            if not diet_followed:
                diet_notes = st.text_area("❌ What did you eat instead?")

            insulin_taken = st.checkbox("💉 Did you take insulin as prescribed?")
            insulin_notes = ""
            if not insulin_taken:
                insulin_notes = st.text_area("❌ Notes on insulin deviation")

            # ----------------------------
            # Blood Sugar Graph
            # ----------------------------
            st.subheader("📈 Blood Sugar Trend")
            fig1, ax1 = plt.subplots()
            ax1.plot(df["datetime"], df["blood sugar measurement (mg/dl)"], marker="o", linestyle="-")
            ax1.set_title("Blood Sugar Over Time")
            ax1.set_xlabel("DateTime")
            ax1.set_ylabel("Blood Sugar (mg/dL)")
            st.pyplot(fig1)

            # ----------------------------
            # Insulin Graph
            # ----------------------------
            st.subheader("💉 Insulin Trend")
            fig2, ax2 = plt.subplots()
            ax2.plot(df["datetime"], df["insulin"], marker="s", linestyle="-", color="orange")
            ax2.set_title("Insulin Usage Over Time")
            ax2.set_xlabel("DateTime")
            ax2.set_ylabel("Insulin (units)")
            st.pyplot(fig2)

            # ----------------------------
            # PDF Report Generation
            # ----------------------------
            if st.button("📄 Generate PDF Report"):
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()
                elements = []

                elements.append(Paragraph("📊 Diabetes Report", styles["Title"]))
                elements.append(Spacer(1, 12))

                # Diet & Insulin Notes
                elements.append(Paragraph(f"Diet Followed: {'Yes' if diet_followed else 'No'}", styles["Normal"]))
                if not diet_followed:
                    elements.append(Paragraph(f"Notes: {diet_notes}", styles["Normal"]))
                elements.append(Spacer(1, 12))

                elements.append(Paragraph(f"Insulin Taken: {'Yes' if insulin_taken else 'No'}", styles["Normal"]))
                if not insulin_taken:
                    elements.append(Paragraph(f"Notes: {insulin_notes}", styles["Normal"]))
                elements.append(Spacer(1, 12))

                # Add table with data
                data_for_table = [df.columns.tolist()] + df.head(10).values.tolist()
                table = Table(data_for_table)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.green),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )
                elements.append(table)

                doc.build(elements)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=buffer,
                    file_name="diabetes_report.pdf",
                    mime="application/pdf",
                )

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
