import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "fitai_pro.db"

st.set_page_config(
    page_title="FITAI PRO | Made by Souvik Dey",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------- Database ---------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_date TEXT NOT NULL,
                workout_name TEXT NOT NULL,
                duration_min INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                description TEXT NOT NULL,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS water (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                water_date TEXT NOT NULL,
                amount_ml INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_date TEXT NOT NULL,
                weight_kg REAL,
                notes TEXT DEFAULT ''
            );
            """
        )


def query_df(query, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute(query, params=()):
    with get_connection() as conn:
        conn.execute(query, params)
        conn.commit()


init_db()

# --------------------------- Styling ---------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.5rem; border-radius: 18px;
        background: linear-gradient(120deg, #102a43, #243b53, #334e68);
        color: white; margin-bottom: 1rem;
    }
    .hero h1 {margin-bottom: .25rem;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 12px; padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------- Sidebar ---------------------------
st.sidebar.markdown("# 💪 FITAI PRO")
st.sidebar.caption("Made by Souvik Dey")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Workout Planner",
        "Workout Logger",
        "Diet Planner",
        "Progress Tracker",
        "Hydration Tracker",
        "AI Fitness Coach",
    ],
)
st.sidebar.divider()
st.sidebar.caption("Fitness education only. Not medical advice.")

# --------------------------- Dashboard ---------------------------
if page == "Dashboard":
    st.markdown(
        '<div class="hero"><h1>FITAI PRO</h1>'
        '<p>Your fitness companion for planning, tracking, and learning.</p>'
        '<p>Made by Souvik Dey</p></div>',
        unsafe_allow_html=True,
    )
    today = date.today().isoformat()
    workouts_today = query_df(
        "SELECT * FROM workouts WHERE workout_date = ?", (today,)
    )
    water_today = query_df(
        "SELECT COALESCE(SUM(amount_ml), 0) AS total FROM water WHERE water_date = ?",
        (today,),
    )
    total_workouts = query_df("SELECT COUNT(*) AS n FROM workouts").iloc[0]["n"]
    total_minutes = query_df(
        "SELECT COALESCE(SUM(duration_min), 0) AS n FROM workouts"
    ).iloc[0]["n"]
    water_total = int(water_today.iloc[0]["total"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Workouts today", int(len(workouts_today)))
    c2.metric("Total workouts logged", int(total_workouts))
    c3.metric("Workout minutes", int(total_minutes))
    c4.metric("Water logged today", f"{water_total:,} ml")
    st.subheader("Quick start")
    st.write("Use the sidebar to plan a workout, log activity, record water, or ask the AI coach.")
    if len(workouts_today):
        st.subheader("Today's workouts")
        st.dataframe(workouts_today, use_container_width=True, hide_index=True)

# --------------------------- Workout Planner ---------------------------
elif page == "Workout Planner":
    st.title("🏋️ Workout Planner")
    st.write("Choose a general routine and adjust it to your comfort and experience.")
    level = st.selectbox("Experience level", ["Beginner", "Intermediate", "Advanced"])
    focus = st.selectbox(
        "Main focus",
        ["General fitness", "Strength", "Cardio", "Mobility and flexibility", "Sports conditioning"],
    )
    days = st.slider("Days available each week", 2, 6, 3)
    templates = {
        "Beginner": [
            ("Full-body basics", "Bodyweight squats, wall/incline push-ups, glute bridges, bird dogs; easy pace."),
            ("Cardio and mobility", "Comfortable walk or cycle, then gentle hip, shoulder, and ankle mobility."),
            ("Full-body basics", "Repeat the first session, using controlled technique and comfortable effort."),
        ],
        "Intermediate": [
            ("Strength A", "Squat variation, push variation, row variation, hip hinge, core stability."),
            ("Cardio", "Moderate cardio at a pace where you can still speak in short sentences."),
            ("Strength B", "Lunge variation, overhead push if appropriate, row, glute bridge, carries."),
            ("Mobility / easy cardio", "Easy movement and mobility; keep the effort comfortable."),
        ],
        "Advanced": [
            ("Strength A", "Planned compound movement patterns, accessory work, and controlled core training."),
            ("Conditioning", "Intervals or steady cardio matched to training history and recovery."),
            ("Strength B", "A balanced full-body session with planned volume and good technique."),
            ("Recovery movement", "Easy cardio and mobility; stop if you experience pain or unusual symptoms."),
        ],
    }
    st.subheader(f"Suggested {days}-day outline")
    for i in range(days):
        name, details = templates[level][i % len(templates[level])]
        if focus == "Cardio" and i % 2 == 0:
            name, details = "Cardio session", "Choose walking, cycling, swimming, or another activity you enjoy."
        elif focus == "Mobility and flexibility":
            name, details = "Mobility session", "Gentle, pain-free mobility for hips, shoulders, ankles, and back."
        st.markdown(f"**Day {i + 1}: {name}**")
        st.write(details)
    st.info("Warm up, use manageable effort, and include rest days. Stop if you feel pain, dizziness, or unusual shortness of breath.")

# --------------------------- Workout Logger ---------------------------
elif page == "Workout Logger":
    st.title("📝 Workout Logger")
    with st.form("workout_form", clear_on_submit=True):
        workout_date = st.date_input("Date", value=date.today())
        workout_name = st.text_input("Workout or activity", placeholder="e.g., Walk, football, full-body session")
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=1440, value=30, step=5)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Save workout")
    if submitted:
        if not workout_name.strip():
            st.error("Enter a workout or activity name.")
        else:
            execute(
                "INSERT INTO workouts (workout_date, workout_name, duration_min, notes) VALUES (?, ?, ?, ?)",
                (workout_date.isoformat(), workout_name.strip(), int(duration), notes.strip()),
            )
            st.success("Workout saved.")
    df = query_df("SELECT * FROM workouts ORDER BY workout_date DESC, id DESC")
    st.subheader("Workout history")
    if df.empty:
        st.info("No workouts logged yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# --------------------------- Diet Planner ---------------------------
elif page == "Diet Planner":
    st.title("🥗 Balanced Meal Planner")
    st.write("These are general meal ideas, not a prescribed diet.")
    preference = st.selectbox("Food preference", ["Vegetarian", "Includes eggs", "Mixed diet"])
    ideas = {
        "Vegetarian": {
            "Breakfast": ["Oats with milk or fortified alternative and fruit", "Vegetable poha with yogurt", "Besan chilla with fruit"],
            "Lunch": ["Dal, rice or roti, and vegetables", "Chickpea bowl with grains and salad", "Paneer/tofu with roti and vegetables"],
            "Snack": ["Fruit and nuts", "Roasted chana", "Yogurt or a suitable alternative"],
            "Dinner": ["Dal, roti, and vegetables", "Bean or lentil curry with rice", "Vegetable khichdi with yogurt"],
        },
        "Includes eggs": {
            "Breakfast": ["Eggs with whole-grain toast and fruit", "Vegetable omelette with toast", "Oats with milk and nuts"],
            "Lunch": ["Dal, rice, and vegetables", "Egg curry with roti and vegetables", "Chickpea bowl with grains and salad"],
            "Snack": ["Fruit and nuts", "Roasted chana", "Yogurt"],
            "Dinner": ["Egg curry, roti, and vegetables", "Dal, rice, and vegetables", "Vegetable khichdi with yogurt"],
        },
        "Mixed diet": {
            "Breakfast": ["Eggs with whole-grain toast and fruit", "Oats with milk and nuts", "Vegetable omelette and toast"],
            "Lunch": ["Rice, chicken, and vegetables", "Roti, dal, and vegetables", "Fish with rice and vegetables"],
            "Snack": ["Fruit and nuts", "Roasted chana", "Yogurt and fruit"],
            "Dinner": ["Chicken, rice, and vegetables", "Egg curry, roti, and vegetables", "Dal, rice, and vegetables"],
        },
    }
    st.caption("Choose meals that fit your culture, budget, allergies, and appetite.")
    for meal, choices in ideas[preference].items():
        st.subheader(meal)
        st.write(" • " + "\n • ".join(choices))
    st.info("Aim for variety and regular meals. If you have allergies, a medical condition, or specific nutrition needs, ask a qualified health professional or registered dietitian.")

# --------------------------- Progress Tracker ---------------------------
elif page == "Progress Tracker":
    st.title("📈 Progress Tracker")
    with st.form("measurement_form", clear_on_submit=True):
        measurement_date = st.date_input("Measurement date", value=date.today())
        weight = st.number_input("Weight in kg (optional; enter 0 to skip)", min_value=0.0, max_value=500.0, value=0.0, step=0.1)
        notes = st.text_input("Other progress notes (optional)", placeholder="e.g., energy, consistency, endurance")
        submitted = st.form_submit_button("Save progress")
    if submitted:
        execute(
            "INSERT INTO measurements (measurement_date, weight_kg, notes) VALUES (?, ?, ?)",
            (measurement_date.isoformat(), weight if weight > 0 else None, notes.strip()),
        )
        st.success("Progress entry saved.")
    df = query_df("SELECT * FROM measurements ORDER BY measurement_date")
    if df.empty:
        st.info("Add an entry to start tracking progress.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        weight_df = df.dropna(subset=["weight_kg"])
        if not weight_df.empty:
            st.subheader("Weight entries over time")
            fig = px.line(weight_df, x="measurement_date", y="weight_kg", markers=True, title="Recorded weight")
            st.plotly_chart(fig, use_container_width=True)
    st.caption("Progress can also mean better stamina, strength, sleep, consistency, or how you feel—not just a number.")

# --------------------------- Hydration Tracker ---------------------------
elif page == "Hydration Tracker":
    st.title("💧 Hydration Tracker")
    today = date.today().isoformat()
    total = int(query_df(
        "SELECT COALESCE(SUM(amount_ml), 0) AS total FROM water WHERE water_date = ?",
        (today,),
    ).iloc[0]["total"])
    st.metric("Water recorded today", f"{total:,} ml")
    with st.form("water_form", clear_on_submit=True):
        amount = st.number_input("Amount of water (ml)", min_value=50, max_value=3000, value=250, step=50)
        water_date = st.date_input("Date", value=date.today())
        submitted = st.form_submit_button("Log water")
    if submitted:
        execute(
            "INSERT INTO water (water_date, amount_ml) VALUES (?, ?)",
            (water_date.isoformat(), int(amount)),
        )
        st.success("Water entry saved.")
        st.rerun()
    df = query_df("SELECT water_date, SUM(amount_ml) AS total_ml FROM water GROUP BY water_date ORDER BY water_date DESC LIMIT 14")
    if not df.empty:
        st.subheader("Recent hydration")
        fig = px.bar(df.sort_values("water_date"), x="water_date", y="total_ml", title="Daily water log")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Hydration needs vary with activity, weather, age, and health. Drink regularly and follow medical advice if you have fluid restrictions.")

# --------------------------- AI Fitness Coach ---------------------------
elif page == "AI Fitness Coach":
    st.title("🤖 FITAI PRO AI Fitness Coach")
    st.write("Ask about balanced workouts, recovery, hydration, or general nutrition.")

    api_key = ""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY", "")

    model = os.getenv("OPENAI_MODEL", "gpt-5.5")
    try:
        secret_model = st.secrets.get("OPENAI_MODEL", "")
        if secret_model:
            model = secret_model
    except Exception:
        pass

    if not api_key:
        st.warning("AI is not configured yet. Add OPENAI_API_KEY in Streamlit Community Cloud → Manage app → Settings → Secrets.")
        st.code('OPENAI_API_KEY = "paste-your-private-key-here"\nOPENAI_MODEL = "your-available-model-name"', language="toml")
        st.caption("Never put your API key in GitHub or share it publicly.")
    else:
        if "fitness_chat_history" not in st.session_state:
            st.session_state.fitness_chat_history = []

        for message in st.session_state.fitness_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input("Ask your fitness coach a question...")
        if question:
            st.session_state.fitness_chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            instructions = (
                "You are FITAI PRO, a friendly fitness education assistant. "
                "Give balanced, practical, age-appropriate advice about exercise, "
                "recovery, hydration, and general nutrition. Do not prescribe extreme "
                "diets, excessive exercise, steroids, or dangerous supplements. Do not "
                "diagnose or treat medical conditions. For injuries, alarming symptoms, "
                "or individual medical concerns, recommend a qualified health professional. "
                "Do not promise specific body changes or guaranteed results."
            )
            try:
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                history = [
                    {"role": item["role"], "content": item["content"]}
                    for item in st.session_state.fitness_chat_history
                ]
                with st.chat_message("assistant"):
                    with st.spinner("Your AI coach is thinking..."):
                        response = client.responses.create(
                            model=model,
                            instructions=instructions,
                            input=history,
                        )
                        answer = response.output_text or "I couldn't generate a response. Please try again."
                        st.markdown(answer)
                st.session_state.fitness_chat_history.append({"role": "assistant", "content": answer})
            except ImportError:
                st.error("The OpenAI package is missing. Add `openai` to requirements.txt and wait for the app to redeploy.")
            except Exception as exc:
                st.error("The AI request failed. Check the API key, API billing, model name/access, and app logs.")
                st.caption(f"Technical details: {exc}")

        if st.button("Clear conversation"):
            st.session_state.fitness_chat_history = []
            st.rerun()

    st.caption("For education only; not medical advice.")

# --------------------------- Footer ---------------------------
st.divider()
st.caption(f"FITAI PRO · Made by Souvik Dey · {datetime.now().year}")
