import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="DiabetCare - Diabetes Management System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #db8ab1;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.8rem;
        color: #df80ff;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #A23B72;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #ff66d9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #b3ff66;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #66ffff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28A745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'blood_sugar_log' not in st.session_state:
    st.session_state.blood_sugar_log = []
if 'meal_log' not in st.session_state:
    st.session_state.meal_log = []

# Main title
st.markdown('<h1 class="main-header">🩺 DiabetCare - Diabetes Management System</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a section:", [
    "🏠 Home",
    "👤 User Profile",
    "💉 Insulin Calculator",
    "🍎 Diet Planner",
    "📊 Blood Sugar Tracker",
    "📈 Analytics",
    "📚 Educational Resources"
])

# HOME PAGE
if page == "🏠 Home":
    st.markdown('<h2 class="section-header">Welcome to DiabetCare</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>💉 Insulin Calculator</h3>
            <p>Calculate your insulin doses based on carb intake, blood sugar levels, and personal factors.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>🍎 Diet Planner</h3>
            <p>Get personalized meal plans and nutritional guidance for better diabetes management.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>📊 Blood Sugar Tracker</h3>
            <p>Monitor and track your blood glucose levels with visual analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Medical Disclaimer</h4>
        <p>This application is for educational and tracking purposes only. Always consult with your healthcare provider 
        before making any changes to your diabetes management plan. This tool does not replace professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)

# USER PROFILE PAGE
elif page == "👤 User Profile":
    st.markdown('<h2 class="section-header">User Profile Setup</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        name = st.text_input("Full Name", value=st.session_state.user_profile.get('name', ''))
        age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.user_profile.get('age', 30))
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=st.session_state.user_profile.get('weight', 70.0))
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=st.session_state.user_profile.get('height', 170.0))
        diabetes_type = st.selectbox("Diabetes Type", ["Type 1", "Type 2", "Gestational"], 
                                   index=["Type 1", "Type 2", "Gestational"].index(st.session_state.user_profile.get('diabetes_type', 'Type 1')))
    
    with col2:
        st.subheader("Insulin Settings")
        carb_ratio = st.number_input("Carbohydrate Ratio (1 unit per X grams)", 
                                   min_value=5.0, max_value=50.0, step=0.5,
                                   value=st.session_state.user_profile.get('carb_ratio', 15.0))
        correction_factor = st.number_input("Correction Factor (1 unit lowers BG by X mg/dL)", 
                                          min_value=10.0, max_value=100.0, step=1.0,
                                          value=st.session_state.user_profile.get('correction_factor', 50.0))
        target_bg = st.number_input("Target Blood Glucose (mg/dL)", 
                                  min_value=80.0, max_value=150.0, step=1.0,
                                  value=st.session_state.user_profile.get('target_bg', 100.0))
        basal_rate = st.number_input("Basal Insulin Rate (units/hour)", 
                                   min_value=0.1, max_value=5.0, step=0.1,
                                   value=st.session_state.user_profile.get('basal_rate', 1.0))
    
    if st.button("Save Profile"):
        st.session_state.user_profile = {
            'name': name,
            'age': age,
            'weight': weight,
            'height': height,
            'diabetes_type': diabetes_type,
            'carb_ratio': carb_ratio,
            'correction_factor': correction_factor,
            'target_bg': target_bg,
            'basal_rate': basal_rate
        }
        st.success("✅ Profile saved successfully!")

# INSULIN CALCULATOR PAGE
elif page == "💉 Insulin Calculator":
    st.markdown('<h2 class="section-header">Insulin Dose Calculator</h2>', unsafe_allow_html=True)
    
    if not st.session_state.user_profile:
        st.warning("⚠️ Please set up your user profile first to use the insulin calculator.")
        st.stop()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Readings")
        current_bg = st.number_input("Current Blood Glucose (mg/dL)", min_value=40.0, max_value=600.0, value=120.0)
        carbs_intake = st.number_input("Carbohydrates to consume (grams)", min_value=0.0, max_value=200.0, value=45.0)
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        
        st.subheader("Additional Factors")
        exercise_planned = st.checkbox("Exercise planned within 2 hours")
        illness = st.checkbox("Currently ill or stressed")
        
    with col2:
        st.subheader("Calculation Results")
        
        # Get user profile data
        profile = st.session_state.user_profile
        
        # Calculate insulin doses
        bolus_for_carbs = carbs_intake / profile['carb_ratio']
        correction_dose = max(0, (current_bg - profile['target_bg']) / profile['correction_factor'])
        
        # Adjust for additional factors
        adjustment_factor = 1.0
        if exercise_planned:
            adjustment_factor *= 0.8  # Reduce by 20% for exercise
        if illness:
            adjustment_factor *= 1.2  # Increase by 20% for illness
        
        total_bolus = (bolus_for_carbs + correction_dose) * adjustment_factor
        
        st.metric("Bolus for Carbs", f"{bolus_for_carbs:.1f} units")
        st.metric("Correction Dose", f"{correction_dose:.1f} units")
        st.metric("**Total Recommended Bolus**", f"**{total_bolus:.1f} units**")
        
        # Display calculation breakdown
        st.markdown("### Calculation Breakdown")
        st.write(f"• Carb Coverage: {carbs_intake}g ÷ {profile['carb_ratio']} = {bolus_for_carbs:.1f} units")
        st.write(f"• Correction: ({current_bg} - {profile['target_bg']}) ÷ {profile['correction_factor']} = {correction_dose:.1f} units")
        if adjustment_factor != 1.0:
            st.write(f"• Adjustment Factor: {adjustment_factor:.1f}")
    
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Important Safety Notes</h4>
        <ul>
            <li>Always verify calculations with your healthcare provider</li>
            <li>Consider timing of previous insulin doses</li>
            <li>Monitor blood glucose levels regularly</li>
            <li>Adjust doses based on your doctor's recommendations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# DIET PLANNER PAGE
elif page == "🍎 Diet Planner":
    st.markdown('<h2 class="section-header">Diabetic Diet Planner</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🥗 Meal Plans", "🍽️ Food Database", "📝 Meal Logger"])
    
    with tab1:
        st.subheader("Recommended Meal Plans")
        
        calorie_target = st.selectbox("Daily Calorie Target", [1200, 1500, 1800, 2000, 2200, 2500])
        meal_preference = st.selectbox("Dietary Preference", ["Balanced", "Low Carb", "Mediterranean", "Vegetarian"])
        
        # Sample meal plans
        meal_plans = {
            "Balanced": {
                "Breakfast": ["2 slices whole grain toast (30g carbs)", "1 scrambled egg", "1/2 avocado", "1 cup unsweetened almond milk"],
                "Lunch": ["Grilled chicken salad (5g carbs)", "Mixed greens", "1 tbsp olive oil dressing", "1 small apple (15g carbs)"],
                "Dinner": ["4oz salmon", "1/2 cup brown rice (22g carbs)", "Steamed broccoli", "1 tsp butter"],
                "Snack": ["1 oz almonds", "1 string cheese"]
            },
            "Low Carb": {
                "Breakfast": ["3 eggs omelet", "Spinach and mushrooms", "1 slice cheese", "1/4 avocado"],
                "Lunch": ["Tuna salad (2g carbs)", "Lettuce wraps", "Cherry tomatoes", "Cucumber slices"],
                "Dinner": ["Grilled steak", "Asparagus", "Caesar salad", "Olive oil"],
                "Snack": ["Hard-boiled egg", "Celery with almond butter"]
            }
        }
        
        if meal_preference in meal_plans:
            plan = meal_plans[meal_preference]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🌅 Breakfast")
                for item in plan["Breakfast"]:
                    st.write(f"• {item}")
                
                st.markdown("#### 🌞 Lunch")
                for item in plan["Lunch"]:
                    st.write(f"• {item}")
            
            with col2:
                st.markdown("#### 🌙 Dinner")
                for item in plan["Dinner"]:
                    st.write(f"• {item}")
                
                st.markdown("#### 🍎 Snack")
                for item in plan["Snack"]:
                    st.write(f"• {item}")
    
    with tab2:
        st.subheader("Food Nutritional Database")
        
        # Sample food database
        food_data = {
            "Food Item": ["Apple (medium)", "White Bread (1 slice)", "Brown Rice (1/2 cup)", "Chicken Breast (3oz)", 
                         "Salmon (3oz)", "Broccoli (1 cup)", "Sweet Potato (medium)", "Almonds (1 oz)"],
            "Carbs (g)": [25, 15, 22, 0, 0, 6, 27, 6],
            "Protein (g)": [0.5, 3, 2.5, 26, 22, 3, 2, 6],
            "Fat (g)": [0.3, 1, 0.9, 3, 11, 0.4, 0.1, 14],
            "Calories": [95, 80, 110, 140, 175, 25, 112, 164],
            "Glycemic Index": [36, 75, 68, 0, 0, 25, 70, 15]
        }
        
        df = pd.DataFrame(food_data)
        st.dataframe(df, use_container_width=True)
        
        # Food search
        search_term = st.text_input("Search for a food item:")
        if search_term:
            filtered_df = df[df["Food Item"].str.contains(search_term, case=False)]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("No matching foods found.")
    
    with tab3:
        st.subheader("Log Your Meals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            meal_date = st.date_input("Date", value=date.today())
            meal_time = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"])
            food_item = st.text_input("Food Item")
            portion_size = st.text_input("Portion Size")
            estimated_carbs = st.number_input("Estimated Carbs (g)", min_value=0.0, step=0.5)
            
            if st.button("Log Meal"):
                meal_entry = {
                    "date": meal_date,
                    "meal": meal_time,
                    "food": food_item,
                    "portion": portion_size,
                    "carbs": estimated_carbs,
                    "timestamp": datetime.now()
                }
                st.session_state.meal_log.append(meal_entry)
                st.success("✅ Meal logged successfully!")
        
        with col2:
            st.subheader("Recent Meal Logs")
            if st.session_state.meal_log:
                recent_meals = st.session_state.meal_log[-5:]  # Show last 5 meals
                for meal in reversed(recent_meals):
                    st.write(f"**{meal['meal']}** - {meal['date']}")
                    st.write(f"• {meal['food']} ({meal['portion']})")
                    st.write(f"• Carbs: {meal['carbs']}g")
                    st.write("---")
            else:
                st.info("No meals logged yet.")

# BLOOD SUGAR TRACKER PAGE
elif page == "📊 Blood Sugar Tracker":
    st.markdown('<h2 class="section-header">Blood Sugar Monitoring</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Log Reading", "📈 View History"])
    
    with tab1:
        st.subheader("Log Blood Sugar Reading")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reading_date = st.date_input("Date", value=date.today())
            reading_time = st.time_input("Time", value=datetime.now().time())
            blood_sugar = st.number_input("Blood Sugar (mg/dL)", min_value=40.0, max_value=600.0, value=100.0)
            reading_type = st.selectbox("Reading Type", 
                                      ["Fasting", "Before Meal", "After Meal", "Bedtime", "Random"])
        
        with col2:
            notes = st.text_area("Notes (optional)", 
                               placeholder="e.g., after exercise, feeling sick, missed medication")
            
            if st.button("Log Reading"):
                reading_entry = {
                    "date": reading_date,
                    "time": reading_time,
                    "value": blood_sugar,
                    "type": reading_type,
                    "notes": notes,
                    "timestamp": datetime.now()
                }
                st.session_state.blood_sugar_log.append(reading_entry)
                st.success("✅ Blood sugar reading logged successfully!")
        
        # Display target ranges
        st.markdown("""
        <div class="info-box">
            <h4>📊 Target Blood Sugar Ranges (mg/dL)</h4>
            <ul>
                <li><strong>Fasting:</strong> 80-130 mg/dL</li>
                <li><strong>Before Meals:</strong> 80-130 mg/dL</li>
                <li><strong>2 hours after meals:</strong> < 180 mg/dL</li>
                <li><strong>Bedtime:</strong> 100-140 mg/dL</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Blood Sugar History")
        
        if st.session_state.blood_sugar_log:
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(st.session_state.blood_sugar_log)
            df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
            
            # Create plot
            fig = go.Figure()
            
            # Add blood sugar readings
            fig.add_trace(go.Scatter(
                x=df['datetime'],
                y=df['value'],
                mode='markers+lines',
                name='Blood Sugar',
                text=df['type'],
                hovertemplate='<b>%{text}</b><br>Value: %{y} mg/dL<br>Date: %{x}<extra></extra>'
            ))
            
            # Add target range
            fig.add_hline(y=130, line_dash="dash", line_color="orange", 
                         annotation_text="Upper Target (130)")
            fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                         annotation_text="Lower Target (80)")
            fig.add_hrect(y0=80, y1=130, fillcolor="lightgreen", opacity=0.2, 
                         annotation_text="Target Range")
            
            fig.update_layout(
                title="Blood Sugar Trends",
                xaxis_title="Date/Time",
                yaxis_title="Blood Sugar (mg/dL)",
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show recent readings table
            st.subheader("Recent Readings")
            recent_df = df.tail(10)[['date', 'time', 'value', 'type', 'notes']]
            st.dataframe(recent_df, use_container_width=True)
            
        else:
            st.info("No blood sugar readings logged yet. Start by logging your first reading!")

# ANALYTICS PAGE
elif page == "📈 Analytics":
    st.markdown('<h2 class="section-header">Health Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    if not st.session_state.blood_sugar_log:
        st.info("No data available yet. Please log some blood sugar readings first.")
        st.stop()
    
    # Convert data to DataFrame
    df = pd.DataFrame(st.session_state.blood_sugar_log)
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_bg = df['value'].mean()
        st.metric("Average BG", f"{avg_bg:.1f} mg/dL")
    
    with col2:
        readings_in_range = len(df[(df['value'] >= 80) & (df['value'] <= 130)])
        total_readings = len(df)
        in_range_pct = (readings_in_range / total_readings) * 100 if total_readings > 0 else 0
        st.metric("Time in Range", f"{in_range_pct:.1f}%")
    
    with col3:
        std_dev = df['value'].std()
        st.metric("Glucose Variability", f"{std_dev:.1f} mg/dL")
    
    with col4:
        total_readings = len(df)
        st.metric("Total Readings", f"{total_readings}")
    
    # Weekly trends
    st.subheader("Weekly Trends")
    df['week'] = df['datetime'].dt.isocalendar().week
    weekly_avg = df.groupby('week')['value'].mean()
    
    fig_weekly = px.line(x=weekly_avg.index, y=weekly_avg.values, 
                        title="Weekly Average Blood Sugar")
    fig_weekly.update_xaxis(title="Week Number")
    fig_weekly.update_yaxis(title="Average Blood Sugar (mg/dL)")
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Distribution by reading type
    st.subheader("Blood Sugar by Reading Type")
    fig_box = px.box(df, x='type', y='value', 
                     title="Blood Sugar Distribution by Reading Type")
    fig_box.update_yaxis(title="Blood Sugar (mg/dL)")
    st.plotly_chart(fig_box, use_container_width=True)

# EDUCATIONAL RESOURCES PAGE
elif page == "📚 Educational Resources":
    st.markdown('<h2 class="section-header">Educational Resources</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 Diabetes Basics", "💉 Insulin Guide", "🍎 Nutrition Tips", "⚠️ Emergency Info"])
    
    with tab1:
        st.subheader("Understanding Diabetes")
        
        st.markdown("""
        ### What is Diabetes?
        Diabetes is a group of metabolic disorders characterized by high blood sugar levels over a prolonged period.
        
        ### Types of Diabetes:
        - **Type 1 Diabetes**: Autoimmune condition where the pancreas produces little or no insulin
        - **Type 2 Diabetes**: Body becomes resistant to insulin or doesn't produce enough insulin
        - **Gestational Diabetes**: Develops during pregnancy
        
        ### Key Management Strategies:
        1. **Blood Sugar Monitoring**: Regular checking helps track glucose levels
        2. **Medication Adherence**: Taking prescribed medications as directed
        3. **Healthy Diet**: Balanced nutrition with carbohydrate counting
        4. **Regular Exercise**: Helps improve insulin sensitivity
        5. **Stress Management**: Stress can affect blood sugar levels
        """)
    
    with tab2:
        st.subheader("Insulin Management Guide")
        
        st.markdown("""
        ### Types of Insulin:
        - **Rapid-acting**: Works within 15 minutes, peaks in 1 hour
        - **Short-acting**: Works within 30 minutes, peaks in 2-3 hours
        - **Intermediate-acting**: Works in 2-4 hours, peaks in 4-12 hours
        - **Long-acting**: Works in several hours, lasts 24+ hours
        
        ### Injection Tips:
        1. Rotate injection sites to prevent lipodystrophy
        2. Use proper injection technique
        3. Check expiration dates
        4. Store insulin properly (refrigerate unopened, room temp when in use)
        
        ### Calculating Insulin Doses:
        - **Carbohydrate Ratio**: Units of insulin per grams of carbs
        - **Correction Factor**: How much 1 unit of insulin lowers blood sugar
        - **Target Range**: Your ideal blood sugar range
        """)
    
    with tab3:
        st.subheader("Nutrition Guidelines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Carbohydrate Counting:
            - 1 carb serving = 15 grams
            - Read nutrition labels carefully
            - Focus on complex carbohydrates
            - Consider glycemic index
            
            ### Recommended Foods:
            - Non-starchy vegetables
            - Lean proteins
            - Whole grains
            - Healthy fats (nuts, avocado, olive oil)
            - Low-fat dairy
            """)
        
        with col2:
            st.markdown("""
            ### Foods to Limit:
            - Sugary drinks and desserts
            - Refined carbohydrates
            - Processed foods high in sodium
            - Trans fats
            - Excessive alcohol
            
            ### Meal Planning Tips:
            - Eat regular, balanced meals
            - Control portion sizes
            - Include protein with each meal
            - Stay hydrated
            - Plan ahead for special occasions
            """)
    
    with tab4:
        st.subheader("Emergency Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="warning-box">
                <h4>🚨 Hypoglycemia (Low Blood Sugar)</h4>
                <p><strong>Symptoms:</strong></p>
                <ul>
                    <li>Shaking, sweating</li>
                    <li>Fast heartbeat</li>
                    <li>Dizziness, confusion</li>
                    <li>Hunger, irritability</li>
                </ul>
                <p><strong>Treatment (15-15 Rule):</strong></p>
                <ol>
                    <li>Take 15g fast-acting carbs</li>
                    <li>Wait 15 minutes</li>
                    <li>Recheck blood sugar</li>
                    <li>Repeat if still low</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-box">
                <h4>🚨 Hyperglycemia (High Blood Sugar)</h4>
                <p><strong>Symptoms:</strong></p>
                <ul>
                    <li>Excessive thirst</li>
                    <li>Frequent urination</li>
                    <li>Fatigue, weakness</li>
                    <li>Blurred vision</li>
                </ul>
                <p><strong>Actions:</strong></p>
                <ol>
                    <li>Check blood sugar</li>
                    <li>Check ketones if over 250 mg/dL</li>
                    <li>Take correction insulin if needed</li>
                    <li>Drink water</li>
                    <li>Call doctor if persistent</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #DC3545; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
            <h3>🚨 EMERGENCY CONTACTS</h3>
            <p><strong>Emergency Services: 911</strong></p>
            <p><strong>Poison Control: 1-800-222-1222</strong></p>
            <p><strong>Your Doctor: _______________</strong></p>
            <p><strong>Pharmacy: _______________</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>DiabetCare - Diabetes Management System</p>
    <p><small>Always consult with healthcare professionals for medical advice. This tool is for educational purposes only.</small></p>
</div>
""", unsafe_allow_html=True)
