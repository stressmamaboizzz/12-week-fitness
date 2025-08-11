import streamlit as st
import pandas as pd

st.set_page_config(page_title="12-Week Fitness Coach", page_icon="💪", layout="centered")

# ====== DATA (embedded – no CSVs needed) ======
# Workout: 12 weeks x 3 sessions/week
weekly_schedule = ["Monday", "Wednesday", "Friday"]
focuses = ["Strength + Hypertrophy", "Cardio HIIT + Core", "Functional + Balance"]
workouts_map = {
    "Strength + Hypertrophy": "Goblet Squat, Smith Incline Press, Lat Pulldown, Dumbbell Romanian Deadlift, Russian Twist",
    "Cardio HIIT + Core": "Jump Squat, Dumbbell Snatch (L/R), Burpee, Plank Row, Dumbbell Swing, Flutter Kicks",
    "Functional + Balance": "Bulgarian Split Squat, One-arm Shoulder Press, Smith Sumo Deadlift, Renegade Row, Single-leg Glute Bridge"
}
workout_rows = []
for week in range(1, 13):
    for day, focus in zip(weekly_schedule, focuses):
        workout_rows.append([f"Week {week}", day, focus, workouts_map[focus]])
workout_df = pd.DataFrame(workout_rows, columns=["Week","Day","Focus","Workout"])

# Meal plan (7 days x 4 meals)
meal_plan = {
    "Day 1": [("Breakfast","Oatmeal + 2 boiled eggs",350,22,30,14),("Lunch","Grilled chicken + brown rice + broccoli",450,40,35,12),("Snack","Greek yogurt + almonds",200,12,10,12),("Dinner","Salmon + veggies + sweet potato",500,38,25,20)],
    "Day 2": [("Breakfast","Protein smoothie (whey, banana, oats)",350,30,30,8),("Lunch","Beef stir-fry + rice + veg",450,35,40,15),("Snack","Boiled egg + fruit",200,10,15,8),("Dinner","Tofu + quinoa + kale salad",500,30,35,18)],
    "Day 3": [("Breakfast","Toast + scrambled eggs + avocado",400,20,25,20),("Lunch","Grilled fish + pumpkin + spinach",450,35,20,15),("Snack","Whey + apple",200,25,15,2),("Dinner","Chicken + brown rice + salad",500,38,35,12)],
    "Day 4": [("Breakfast","Yogurt + granola + berries",350,20,30,10),("Lunch","Turkey + couscous + steamed veg",450,35,30,12),("Snack","Protein bar",200,20,15,6),("Dinner","Beef + veg + mashed cauliflower",500,35,25,18)],
    "Day 5": [("Breakfast","Egg white omelet + toast",350,25,25,10),("Lunch","Shrimp + rice noodles + bok choy",450,30,40,12),("Snack","Low-fat milk + banana",200,10,25,5),("Dinner","Grilled chicken + sweet potato + greens",500,35,30,15)],
    "Day 6": [("Breakfast","Cottage cheese + pear + walnuts",350,25,25,12),("Lunch","Tuna salad + toast + soup",450,35,25,15),("Snack","Protein shake",200,25,10,2),("Dinner","Lean pork + rice + sautéed spinach",500,38,35,15)],
    "Day 7": [("Breakfast","Oatmeal + peanut butter + egg",350,22,30,14),("Lunch","Grilled tofu + rice + cabbage slaw",450,30,35,15),("Snack","Boiled egg + nuts",200,12,5,14),("Dinner","Steamed fish + veg + brown rice",500,36,30,16)]
}
meal_entries = []
for day, meals in meal_plan.items():
    for meal in meals:
        meal_entries.append([day, *meal])
meal_df = pd.DataFrame(meal_entries, columns=["Day","Meal Time","Food","Calories","Protein (g)","Carbs (g)","Fats (g)"])

# Progress template (editable in-session; downloadable as CSV)
progress_df = pd.DataFrame([[f"Week {w}","","","","","","",""] for w in range(1,13)],
    columns=["Week","Body Weight (kg)","Body Fat (%)","Waist (cm)","Hip (cm)","Workout Sessions","Energy Level (1-5)","Notes"])

# ====== THEME (dark) via CSS – no config file needed ======
st.markdown("""
<style>
:root { --accent: #00B487; }
a, .st-emotion-cache-1dp5vir { color: var(--accent) !important; }
.stButton>button { background: rgba(0,180,135,0.12); border: 1px solid var(--accent); color: #E6FFF7; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ====== UI ======
st.title("💪 12-Week Fitness Coach")
st.caption("Optimized for iPhone & iPad — 3 sessions/week • 50' per session (Dark Mode)")

with st.sidebar:
    st.header("Targets")
    st.markdown("""
- Weight: 79 → **67 kg**
- Body Fat: 27% → **~18–20%**
- Frequency: **3x/week**, 50’ per session
- Equipment: Dumbbell • Lat Pulldown • Smith
""")
    st.markdown("---")
    st.write("Data export")
    st.download_button("Workout CSV", workout_df.to_csv(index=False), file_name="workout_plan.csv")
    st.download_button("Meal CSV", meal_df.to_csv(index=False), file_name="meal_plan.csv")
    st.download_button("Progress CSV (blank)", progress_df.to_csv(index=False), file_name="progress_tracker.csv")

tab1, tab2, tab3 = st.tabs(["📅 Workout", "🍽️ Meal Plan", "📈 Progress"])

with tab1:
    st.subheader("Weekly Schedule")
    week_list = sorted(workout_df["Week"].unique(), key=lambda x: int(x.split()[-1]))
    selected_week = st.selectbox("Choose Week", week_list, index=0)
    wdf = workout_df[workout_df["Week"] == selected_week]
    for _, row in wdf.iterrows():
        with st.expander(f"{row['Day']} — {row['Focus']}"):
            st.markdown("**Routine:**")
            for it in [x.strip() for x in row["Workout"].split(",")]:
                st.markdown(f"- {it}")
            st.markdown("**Protocol:** 3 sets each, 8–15 reps. Rest 30–60s.")
            st.checkbox(f"Completed: {row['Day']}", key=f"done_{selected_week}_{row['Day']}")

with tab2:
    st.subheader("7-Day Fat Loss Menu (≈1500–1600 kcal/day)")
    day_names = list(meal_df["Day"].unique())
    sel_day = st.selectbox("Day", day_names, index=0)
    mdf = meal_df[meal_df["Day"] == sel_day]
    st.dataframe(mdf, use_container_width=True)
    st.markdown(f"**Daily total:** {int(mdf['Calories'].sum())} kcal • Protein {int(mdf['Protein (g)'].sum())} g")

with tab3:
    st.subheader("Weekly Check-in")
    # keep a copy in session
    if "progress_state" not in st.session_state:
        st.session_state["progress_state"] = progress_df.copy()
    p = st.session_state["progress_state"]
    week_select = st.selectbox("Week", p["Week"].tolist(), index=0)
    row_idx = p[p["Week"] == week_select].index[0]

    c1, c2 = st.columns(2)
    with c1:
        weight = st.number_input("Body Weight (kg)", min_value=0.0, value=79.0, step=0.1)
        bodyfat = st.number_input("Body Fat (%)", min_value=0.0, value=27.0, step=0.1)
        energy = st.slider("Energy (1–5)", 1, 5, 3)
    with c2:
        waist = st.number_input("Waist (cm)", min_value=0.0, value=85.0, step=0.5)
        hip = st.number_input("Hip (cm)", min_value=0.0, value=95.0, step=0.5)
        sessions = st.number_input("Workout Sessions", min_value=0, max_value=3, value=0, step=1)

    notes = st.text_area("Notes", value="", height=80)

    if st.button("Save Week Data"):
        p.loc[row_idx, ["Body Weight (kg)","Body Fat (%)","Waist (cm)","Hip (cm)","Workout Sessions","Energy Level (1-5)","Notes"]] = [
            weight, bodyfat, waist, hip, sessions, energy, notes
        ]
        st.success("Saved in session. Use download to export.")
    st.download_button("⬇️ Download Updated Progress CSV", p.to_csv(index=False), file_name="progress_tracker_updated.csv")

st.caption("Tip: Add this page to your iPhone/iPad Home Screen for an app-like experience.")
