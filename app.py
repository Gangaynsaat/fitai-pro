import sqlite3
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "fitai.db"

st.set_page_config(page_title="FITAI PRO | Souvik Dey", page_icon="💪", layout="wide")

st.markdown("""
<style>
.stApp { background: #0b0f14; color: #f4f7fb; }
[data-testid="stSidebar"] { background: #101820; }
.hero {
  padding: 1.5rem 1.7rem; border-radius: 18px;
  background: linear-gradient(120deg, #142a24, #142033 70%, #1a182c);
  border: 1px solid #2b453c; margin-bottom: 1rem;
}
.hero h1 { margin: 0; color: #f5fff8; font-size: 2.5rem; }
.hero p { margin: .4rem 0 0 0; color: #a8f0c5; }
div[data-testid="stMetric"] { background: #111922; padding: 1rem; border-radius: 12px; border: 1px solid #26333e; }
</style>
""", unsafe_allow_html=True)

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_date TEXT NOT NULL, exercise TEXT NOT NULL,
            sets INTEGER NOT NULL, reps INTEGER NOT NULL,
            weight REAL NOT NULL DEFAULT 0, notes TEXT DEFAULT ''
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measurement_date TEXT NOT NULL, weight REAL NOT NULL, notes TEXT DEFAULT ''
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS hydration (
            id INTEGER PRIMARY KEY AUTOINCREMENT, water_date TEXT NOT NULL, amount_ml INTEGER NOT NULL
        )""")

def read_sql(query, params=()):
    with connect() as conn:
        return pd.read_sql_query(query, conn, params=params)

init_db()

WORKOUTS = {
    "Full Body": {
        "Beginner": [
            ("Bodyweight squat", "2 × 8–12"), ("Wall/incline push-up", "2 × 8–12"),
            ("Glute bridge", "2 × 10"), ("Bird dog", "2 × 8 each side"),
            ("Easy walk", "10–20 minutes"),
        ],
        "Intermediate": [
            ("Goblet squat", "3 × 8–12"), ("Dumbbell row", "3 × 8–12"),
            ("Dumbbell chest press", "3 × 8–12"), ("Romanian deadlift", "3 × 8–10"),
            ("Plank", "3 comfortable holds"),
        ],
    },
    "Upper Body": {
        "Beginner": [
            ("Wall/incline push-up", "2 × 8–12"), ("Resistance-band row", "2 × 10"),
            ("Light shoulder press", "2 × 8"), ("Biceps curl", "2 × 10"),
        ],
        "Intermediate": [
            ("Dumbbell bench press", "3 × 8–12"), ("Lat pulldown", "3 × 8–12"),
            ("Seated cable row", "3 × 10"), ("Shoulder press", "3 × 8–10"),
            ("Biceps curl", "2 × 10–12"),
        ],
    },
    "Lower Body": {
        "Beginner": [
            ("Bodyweight squat", "2 × 10"), ("Glute bridge", "2 × 10"),
            ("Supported split squat", "2 × 6 each side"), ("Calf raise", "2 × 12"),
        ],
        "Intermediate": [
            ("Squat", "3 × 8–10"), ("Romanian deadlift", "3 × 8–10"),
            ("Leg press", "3 × 10"), ("Leg curl", "3 × 10"), ("Calf raise", "3 × 12"),
        ],
    },
}

MEALS = {
    "Vegetarian": {
        "Breakfast": ["Oats with milk, banana and nuts", "Vegetable poha with curd", "Idli with sambar"],
        "Lunch": ["Rice, dal, vegetables and curd", "Roti, paneer and vegetables", "Rajma, rice and salad"],
        "Snack": ["Fruit and yogurt", "Roasted chana", "Milk and nuts"],
        "Dinner": ["Roti, dal and vegetables", "Paneer, rice and vegetables", "Khichdi with curd"],
    },
    "Non-vegetarian": {
        "Breakfast": ["Eggs, whole-grain toast and fruit", "Oats with milk and nuts", "Vegetable omelette and toast"],
        "Lunch": ["Rice, chicken and vegetables", "Roti, eggs and vegetables", "Fish, rice and vegetables"],
        "Snack": ["Yogurt and fruit", "Roasted chana", "Milk and nuts"],
        "Dinner": ["Chicken, rice and vegetables", "Egg curry, roti and vegetables", "Dal, rice and vegetables"],
    },
}

st.sidebar.markdown("## 💪 FITAI PRO")
st.sidebar.caption("Made by Souvik Dey")
page = st.sidebar.radio("Navigate", [
    "Dashboard", "Workout Planner", "Workout Logger", "Diet Planner",
    "Progress Tracker", "Hydration Tracker", "AI Fitness Coach"
])
st.sidebar.markdown("---")
st.sidebar.caption("Fitness education only. Not medical advice.")

if page == "Dashboard":
    st.markdown('<div class="hero"><h1>FITAI PRO</h1><p>AI-powered fitness companion · Made by Souvik Dey</p></div>', unsafe_allow_html=True)
    today = date.today().isoformat()
    workouts = read_sql("SELECT * FROM workouts")
    todays = read_sql("SELECT * FROM workouts WHERE workout_date=?", (today,))
    measurements = read_sql("SELECT * FROM measurements ORDER BY measurement_date, id")
    water = read_sql("SELECT COALESCE(SUM(amount_ml),0) AS total FROM hydration WHERE water_date=?", (today,))
    a, b, c, d = st.columns(4)
    a.metric("Workout entries today", len(todays))
    b.metric("Total logged entries", len(workouts))
    c.metric("Latest recorded weight", f"{measurements.iloc[-1]['weight']:.1f} kg" if not measurements.empty else "—")
    d.metric("Water logged today", f"{int(water.iloc[0]['total'])} ml")
    st.subheader("Your fitness workspace")
    st.write("Plan a manageable workout, record what you complete, and review your consistency over time.")
    st.info("Start at a comfortable level, learn safe technique, allow recovery, and avoid extreme diets or training through pain.")
    if not workouts.empty:
        st.subheader("Recent workout entries")
        st.dataframe(workouts.sort_values(["workout_date", "id"], ascending=False).head(8), use_container_width=True, hide_index=True)
    else:
        st.caption("Your workout history will appear here after you log your first session.")

elif page == "Workout Planner":
    st.title("🏋️ Workout Planner")
    kind = st.selectbox("Workout focus", list(WORKOUTS))
    level = st.selectbox("Experience", ["Beginner", "Intermediate"])
    st.caption("Use only exercises suitable for your ability and equipment.")
    for name, prescription in WORKOUTS[kind][level]:
        st.write(f"**{name}** — {prescription}")
    st.subheader("Example weekly rhythm")
    st.dataframe(pd.DataFrame({
        "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "Activity": ["Strength session", "Easy walk / preferred sport", "Recovery / mobility",
                     "Strength session", "Easy cardio", "Optional enjoyable activity", "Rest"],
    }), use_container_width=True, hide_index=True)
    st.warning("This is a general template, not an individualized medical plan. Stop if you experience pain, dizziness, or unusual symptoms.")

elif page == "Workout Logger":
    st.title("📝 Workout Logger")
    with st.form("workout_form", clear_on_submit=True):
        d = st.date_input("Date", value=date.today())
        exercise = st.text_input("Exercise name", placeholder="e.g. Goblet squat")
        c1, c2, c3 = st.columns(3)
        sets = c1.number_input("Sets", 1, 30, 3)
        reps = c2.number_input("Reps per set", 1, 200, 10)
        weight = c3.number_input("External weight (kg)", 0.0, 1000.0, 0.0, 1.0)
        notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("Save workout")
        if submitted:
            if not exercise.strip():
                st.error("Please enter an exercise name.")
            else:
                with connect() as conn:
                    conn.execute("INSERT INTO workouts (workout_date, exercise, sets, reps, weight, notes) VALUES (?, ?, ?, ?, ?, ?)",
                                 (d.isoformat(), exercise.strip(), int(sets), int(reps), float(weight), notes.strip()))
                st.success("Workout saved.")
                st.rerun()
    history = read_sql("SELECT * FROM workouts ORDER BY workout_date DESC, id DESC")
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
        st.download_button("Download workout CSV", history.to_csv(index=False).encode(), "fitai_workouts.csv", "text/csv")
        ids = history["id"].tolist()
        delete_id = st.selectbox("Select an entry to delete", ids)
        if st.button("Delete selected entry"):
            with connect() as conn:
                conn.execute("DELETE FROM workouts WHERE id=?", (int(delete_id),))
            st.success("Entry deleted.")
            st.rerun()
    else:
        st.caption("No workouts logged yet.")

elif page == "Diet Planner":
    st.title("🥗 Balanced Meal Ideas")
    diet = st.selectbox("Food preference", ["Vegetarian", "Non-vegetarian"])
    st.caption("Choose options that fit your culture, budget, allergies and appetite.")
    for meal, options in MEALS[diet].items():
        st.subheader(meal)
        st.selectbox(f"{meal} idea", options, key=f"{diet}_{meal}")
    st.subheader("Balanced nutrition reminders")
    st.markdown("- Include a variety of vegetables and fruit.\n- Include protein sources such as dal, beans, milk, curd, paneer, eggs, fish or chicken as suitable.\n- Include grains or other carbohydrate sources and suitable fats.\n- Drink water regularly and eat regular meals.")
    st.info("These are meal ideas, not a calculated diet. Avoid extreme restriction. For allergies, medical conditions or specific nutrition needs, consult a registered dietitian or clinician.")

elif page == "Progress Tracker":
    st.title("📈 Progress Tracker")
    with st.form("measurement_form", clear_on_submit=True):
        d = st.date_input("Record date", value=date.today())
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=60.0, step=0.5)
        notes = st.text_input("Optional note", placeholder="Energy, strength, or general observations")
        submitted = st.form_submit_button("Save record")
        if submitted:
            with connect() as conn:
                conn.execute("INSERT INTO measurements (measurement_date, weight, notes) VALUES (?, ?, ?)",
                             (d.isoformat(), float(weight), notes.strip()))
            st.success("Record saved.")
            st.rerun()
    data = read_sql("SELECT * FROM measurements ORDER BY measurement_date, id")
    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)
        fig = px.line(data, x="measurement_date", y="weight", markers=True, title="Recorded weight history",
                      labels={"measurement_date": "Date", "weight": "Weight (kg)"})
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("Export progress CSV", data.to_csv(index=False).encode(), "fitai_progress.csv", "text/csv")
    else:
        st.caption("Add a record to begin your history.")

elif page == "Hydration Tracker":
    st.title("💧 Hydration Tracker")
    amount = st.selectbox("Water amount (ml)", [150, 200, 250, 300, 500, 750], index=2)
    if st.button("Record water"):
        with connect() as conn:
            conn.execute("INSERT INTO hydration (water_date, amount_ml) VALUES (?, ?)", (date.today().isoformat(), int(amount)))
        st.success(f"Recorded {amount} ml.")
        st.rerun()
    total = read_sql("SELECT COALESCE(SUM(amount_ml),0) AS total FROM hydration WHERE water_date=?", (date.today().isoformat(),))
    st.metric("Water logged today", f"{int(total.iloc[0]['total'])} ml")
    hist = read_sql("SELECT water_date, SUM(amount_ml) AS total_ml FROM hydration GROUP BY water_date ORDER BY water_date")
    if not hist.empty:
        st.plotly_chart(px.bar(hist, x="water_date", y="total_ml", title="Daily water log"), use_container_width=True)


elif page == "AI Fitness Coach":    
    import os
    from openai import OpenAI


st.title("🤖 FITAI PRO AI Fitness Coach")
st.write("Ask your AI coach about workouts, balanced nutrition, recovery, and fitness routines.")

try:
    api_key = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    st.warning("AI is not configured yet. Add OPENAI_API_KEY in Streamlit Settings → Secrets.")
else:
    if "fitness_chat_history" not in st.session_state:
        st.session_state.fitness_chat_history = []

    for message in st.session_state.fitness_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask your fitness coach a question...")

    if question:
        st.session_state.fitness_chat_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        instructions = (
            "You are FITAI PRO, a helpful fitness education assistant. "
            "Give practical, balanced advice about exercise, recovery, "
            "hydration, and general nutrition. Avoid extreme diets, "
            "dangerous supplements, steroids, and excessive exercise. "
            "Do not diagnose medical conditions. Recommend a qualified "
            "health professional for injuries or concerning symptoms. "
            "Keep advice age-appropriate."
        )

        try:
            client = OpenAI(api_key=api_key)

            with st.chat_message("assistant"):
                with st.spinner("Your AI coach is thinking..."):
                    conversation = [
                        {
                            "role": item["role"],
                            "content": item["content"]
                        }
                        for item in st.session_state.fitness_chat_history
                    ]

                    response = client.responses.create(
                        model="gpt-5.5",
                        instructions=instructions,
                        input=conversation
                    )

                    answer = response.output_text
                    st.markdown(answer)

            st.session_state.fitness_chat_history.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as error:
            st.error(
                "AI request failed. Check your API key, API billing, "
                "model availability, and internet connection."
            )
            st.caption(f"Technical details: {error}")

    if st.button("Clear conversation"):
        st.session_state.fitness_chat_history = []
        st.rerun()

st.caption(
    "For educational purposes only; this is not medical advice."
)
```


    st.title("🤖 Fitness Coach")
    st.info("This starter coach uses a built-in knowledge base; it is not yet connected to a live AI model.")
    question = st.text_area("Ask a fitness question", placeholder="How can I organize a balanced weekly workout?")
    if st.button("Get advice"):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            q = question.lower()
            if any(x in q for x in ["food", "diet", "nutrition", "protein", "meal"]):
                answer = "Aim for varied, regular meals with suitable protein sources, grains or other carbohydrates, vegetables, fruit and fats. Adapt foods to your preferences, allergies and needs; avoid extreme dieting."
            elif any(x in q for x in ["workout", "exercise", "gym", "training", "muscle"]):
                answer = "Choose manageable exercises, learn correct technique, cover major muscle groups across the week, and increase difficulty gradually only when your current routine feels comfortable. Allow recovery."
            elif any(x in q for x in ["rest", "recovery", "sleep", "tired"]):
                answer = "Recovery is part of training. Keep a regular sleep routine, take rest when needed, eat adequately, and reduce activity if fatigue persists. Seek medical advice for concerning symptoms."
            else:
                answer = "Set a realistic goal, choose a consistent and safe routine, record what you do, and review progress periodically. For injury or medical concerns, consult a qualified professional."
            st.subheader("Coach response")
            st.write(answer)
    st.caption("For educational purposes only; not a diagnosis or substitute for a qualified health professional.")

st.divider()
st.caption(f"FITAI PRO · Made by Souvik Dey · {datetime.now().year}")
