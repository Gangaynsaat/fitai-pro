import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "fitai_pro.db"

st.set_page_config(
    page_title="FITAI PRO 3D | Made by Souvik Dey",
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    .stApp {font-family: Inter, sans-serif;}
    .block-container {padding-top: 1.25rem; padding-bottom: 2rem; max-width: 1500px;}
    .hero {padding: 2rem; border-radius: 24px; color: white; margin-bottom: 1rem;
      background: radial-gradient(circle at 85% 15%, rgba(0,255,209,.23), transparent 28%),
      linear-gradient(120deg, #081526, #102c43 58%, #164e63); border: 1px solid rgba(103,232,249,.25);
      box-shadow: 0 18px 50px rgba(0,0,0,.18);}
    .hero h1 {font-size: clamp(2rem, 4vw, 3.5rem); letter-spacing: -.05em; margin: 0; font-weight: 900;}
    .hero p {color: #d4f7ff; margin-bottom: .25rem;}
    .eyebrow {text-transform: uppercase; letter-spacing: .18em; color: #67e8f9; font-size: .75rem; font-weight: 800;}
    div[data-testid="stMetric"] {background: linear-gradient(145deg, rgba(20,50,72,.12), rgba(20,50,72,.03));
      border: 1px solid rgba(103,232,249,.22); border-radius: 16px; padding: 15px;}
    div[data-testid="stMetricLabel"] {font-weight: 600;}
    .stButton button, .stFormSubmitButton button {border-radius: 12px; font-weight: 700;}
    section[data-testid="stSidebar"] {border-right: 1px solid rgba(103,232,249,.16);}
    div[data-testid="stExpander"] {border-radius: 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def fitness_3d_scene():
    """A lightweight interactive 3D fitness-themed figure; no external 3D assets required."""
    # Approximate mannequin made from connected 3D points, with orbiting data nodes.
    points = {
        "head": (0, 0, 3.25), "neck": (0, 0, 2.85), "chest": (0, 0, 2.35),
        "waist": (0, 0, 1.75), "hip": (0, 0, 1.35),
        "l_shoulder": (-0.48, 0, 2.65), "l_elbow": (-0.78, 0.05, 2.15), "l_hand": (-0.9, 0.08, 1.65),
        "r_shoulder": (0.48, 0, 2.65), "r_elbow": (0.78, 0.05, 2.15), "r_hand": (0.9, 0.08, 1.65),
        "l_knee": (-0.28, 0, 0.7), "l_foot": (-0.32, 0.18, 0.05),
        "r_knee": (0.28, 0, 0.7), "r_foot": (0.32, 0.18, 0.05),
    }
    bones = [("head","neck"),("neck","chest"),("chest","waist"),("waist","hip"),
             ("neck","l_shoulder"),("l_shoulder","l_elbow"),("l_elbow","l_hand"),
             ("neck","r_shoulder"),("r_shoulder","r_elbow"),("r_elbow","r_hand"),
             ("hip","l_knee"),("l_knee","l_foot"),("hip","r_knee"),("r_knee","r_foot")]
    fig = go.Figure()
    for a,b in bones:
        fig.add_trace(go.Scatter3d(x=[points[a][0],points[b][0]], y=[points[a][1],points[b][1]], z=[points[a][2],points[b][2]],
            mode='lines', line=dict(color='#67e8f9', width=8), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter3d(x=[v[0] for v in points.values()], y=[v[1] for v in points.values()], z=[v[2] for v in points.values()],
        mode='markers', marker=dict(size=5, color='#a7f3d0', line=dict(color='#ffffff', width=1)),
        text=list(points.keys()), hovertemplate='%{text}<extra></extra>', showlegend=False))
    # Three orbit rings and satellite points add depth and a futuristic dashboard look.
    import math
    for radius, zlev in [(1.25, 1.6), (1.05, 2.45), (1.5, 0.9)]:
        t=[i*2*math.pi/90 for i in range(91)]
        fig.add_trace(go.Scatter3d(x=[radius*math.cos(v) for v in t], y=[.15+radius*.42*math.sin(v) for v in t], z=[zlev+.12*math.sin(v*2) for v in t],
            mode='lines', line=dict(color='rgba(103,232,249,0.35)', width=2), hoverinfo='skip', showlegend=False))
    fig.update_layout(height=440, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)',
        scene=dict(bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False, range=[-1.8,1.8]),
        yaxis=dict(visible=False, range=[-1.8,1.8]), zaxis=dict(visible=False, range=[-0.3,3.8]),
        aspectmode='manual', aspectratio=dict(x=1,y=1,z=1.2), camera=dict(eye=dict(x=1.6,y=1.8,z=1.2))),
        showlegend=False)
    return fig


# --------------------------- Animated 3D trainer ---------------------------
MUSCLE_MOVES = {
    "Chest": {"exercise":"Push-up pattern", "primary":"Chest, triceps, front shoulders", "sets":"2–3 comfortable sets", "reps":"6–12 controlled reps", "tip":"Keep your body in one steady line; use a wall or bench incline to make it easier."},
    "Back": {"exercise":"Bent-over row pattern", "primary":"Upper back, lats, rear shoulders, biceps", "sets":"2–3 comfortable sets", "reps":"8–12 controlled reps", "tip":"Hinge at the hips with a neutral back. Use a very light load or a no-weight practice first."},
    "Shoulders": {"exercise":"Overhead press pattern", "primary":"Shoulders, triceps, upper chest", "sets":"2–3 comfortable sets", "reps":"6–12 controlled reps", "tip":"Keep ribs relaxed and move only through a comfortable range. No need to use heavy weights."},
    "Biceps": {"exercise":"Biceps curl pattern", "primary":"Biceps and forearms", "sets":"2 comfortable sets", "reps":"8–12 controlled reps", "tip":"Keep elbows near your sides and avoid swinging your torso."},
    "Triceps": {"exercise":"Triceps extension pattern", "primary":"Triceps", "sets":"2 comfortable sets", "reps":"8–12 controlled reps", "tip":"Keep upper arms steady and stop if elbows or shoulders hurt."},
    "Legs / Quads": {"exercise":"Bodyweight squat", "primary":"Quadriceps, hamstrings, glutes", "sets":"2–3 comfortable sets", "reps":"8–12 controlled reps", "tip":"Sit hips back, keep feet stable, and use a chair target if helpful."},
    "Glutes": {"exercise":"Glute bridge pattern", "primary":"Glutes and hamstrings", "sets":"2 comfortable sets", "reps":"8–12 controlled reps", "tip":"Lift hips smoothly without forcing your lower back into an arch."},
    "Core / Abs": {"exercise":"Standing core brace / crunch pattern", "primary":"Abdominals and trunk stabilisers", "sets":"2 comfortable sets", "reps":"6–10 slow reps", "tip":"Breathe normally and move gently; stop if you feel back or neck pain."},
    "Calves": {"exercise":"Calf raise", "primary":"Calves and ankle stabilisers", "sets":"2 comfortable sets", "reps":"10–15 controlled reps", "tip":"Hold a stable support if needed and rise only as high as comfortable."},
    "Full body": {"exercise":"Bodyweight squat pattern", "primary":"Legs, glutes, trunk and balance", "sets":"2 easy sets", "reps":"6–10 controlled reps", "tip":"Use a comfortable range, steady breathing, and rest when needed."},
}


def trainer_points(muscle, phase):
    """Return a simple full-body 3D articulated mannequin pose for a motion preview."""
    import math
    a = math.sin(phase)
    pts = {
        "head": (0, 0, 3.35), "neck": (0, 0, 3.02), "shoulderL": (-0.43, 0, 2.82),
        "shoulderR": (0.43, 0, 2.82), "elbowL": (-0.62, 0, 2.35), "elbowR": (0.62, 0, 2.35),
        "handL": (-0.67, 0, 1.95), "handR": (0.67, 0, 1.95), "chest": (0, 0, 2.65),
        "waist": (0, 0, 2.02), "hip": (0, 0, 1.82), "hipL": (-0.22, 0, 1.78), "hipR": (0.22, 0, 1.78),
        "kneeL": (-0.25, 0, 0.95), "kneeR": (0.25, 0, 0.95), "ankleL": (-0.28, 0, 0.16), "ankleR": (0.28, 0, 0.16),
        "toeL": (-0.32, 0.25, 0.1), "toeR": (0.32, 0.25, 0.1),
    }
    # Keep the mannequin's movement readable and deliberately simplified for teaching.
    if muscle == "Legs / Quads" or muscle == "Full body":
        bend = 0.30 * (1 + a) / 2
        pts["hip"] = (0, 0, 1.82 - bend * .55); pts["hipL"] = (-.22, 0, 1.78 - bend * .55); pts["hipR"] = (.22, 0, 1.78 - bend * .55)
        pts["chest"] = (0, 0, 2.65 - bend * .48); pts["neck"] = (0, 0, 3.02 - bend * .48); pts["head"] = (0, 0, 3.35 - bend * .48)
        pts["kneeL"] = (-.40, 0, .95 - bend * .18); pts["kneeR"] = (.40, 0, .95 - bend * .18)
    elif muscle == "Shoulders":
        lift = (1 + a) / 2
        pts["elbowL"] = (-.72, 0, 2.42 + .55 * lift); pts["elbowR"] = (.72, 0, 2.42 + .55 * lift)
        pts["handL"] = (-.72, 0, 2.05 + .95 * lift); pts["handR"] = (.72, 0, 2.05 + .95 * lift)
    elif muscle == "Biceps":
        curl = (1 + a) / 2
        pts["elbowL"] = (-.65, 0, 2.35); pts["elbowR"] = (.65, 0, 2.35)
        pts["handL"] = (-.62, -.03, 1.95 + .48 * curl); pts["handR"] = (.62, -.03, 1.95 + .48 * curl)
    elif muscle == "Triceps":
        ext = (1 + a) / 2
        pts["elbowL"] = (-.56, 0, 2.45 + .15 * ext); pts["elbowR"] = (.56, 0, 2.45 + .15 * ext)
        pts["handL"] = (-.65, 0, 2.05 + .45 * ext); pts["handR"] = (.65, 0, 2.05 + .45 * ext)
    elif muscle == "Back":
        row = (1 + a) / 2
        for key in ["head", "neck", "shoulderL", "shoulderR", "chest", "waist"]:
            x,y,z=pts[key]; pts[key]=(x, y + .18*row, z - (.18*row if key in ["head","neck","chest"] else 0))
        pts["elbowL"] = (-.72, -.1, 2.36); pts["elbowR"] = (.72, -.1, 2.36)
        pts["handL"] = (-.45, -.22 + .3*row, 2.28); pts["handR"] = (.45, -.22 + .3*row, 2.28)
    elif muscle == "Chest":
        push = (1 + a) / 2
        pts["chest"]=(0,.15*push,2.62); pts["waist"]=(0,.15*push,2.00); pts["hip"]=(0,.15*push,1.82)
        pts["shoulderL"] = (-.43,.15*push,2.78); pts["shoulderR"]=(.43,.15*push,2.78)
        pts["elbowL"] = (-.68, -.15 + .22*push, 2.5); pts["elbowR"]=(.68,-.15 + .22*push,2.5)
        pts["handL"] = (-.70, -.2 + .28*push, 2.25); pts["handR"]=(.70,-.2 + .28*push,2.25)
    elif muscle == "Glutes":
        lift = (1 + a) / 2
        pts["hip"]=(0,0,1.55+.35*lift); pts["hipL"]=(-.22,0,1.52+.35*lift); pts["hipR"]=(.22,0,1.52+.35*lift)
        pts["waist"]=(0,0,1.78+.30*lift); pts["chest"]=(0,0,2.10+.25*lift); pts["neck"]=(0,0,2.42+.25*lift); pts["head"]=(0,0,2.75+.25*lift)
        pts["kneeL"] = (-.48,0,.65); pts["kneeR"]=(.48,0,.65)
    elif muscle == "Core / Abs":
        crunch=(1+a)/2
        pts["chest"]=(0,.08*crunch,2.65-.28*crunch); pts["neck"]=(0,.1*crunch,3.02-.22*crunch); pts["head"]=(0,.12*crunch,3.35-.18*crunch)
    elif muscle == "Calves":
        rise=(1+a)/2*.24
        pts["ankleL"]=(-.28,0,.16+rise); pts["ankleR"]=(.28,0,.16+rise); pts["kneeL"]=(-.25,0,.95+rise); pts["kneeR"]=(.25,0,.95+rise)
    return pts


def animated_trainer(muscle):
    import math
    names = ["head","neck","chest","waist","hip","shoulderL","elbowL","handL","shoulderR","elbowR","handR","hipL","kneeL","ankleL","toeL","hipR","kneeR","ankleR","toeR"]
    bones = [("head","neck"),("neck","chest"),("chest","waist"),("waist","hip"),("neck","shoulderL"),("shoulderL","elbowL"),("elbowL","handL"),("neck","shoulderR"),("shoulderR","elbowR"),("elbowR","handR"),("hip","hipL"),("hipL","kneeL"),("kneeL","ankleL"),("ankleL","toeL"),("hip","hipR"),("hipR","kneeR"),("kneeR","ankleR"),("ankleR","toeR")]
    def coords(phase):
        pts=trainer_points(muscle,phase)
        xs=[]; ys=[]; zs=[]
        for u,v in bones:
            for key in (u,v):
                x,y,z=pts[key]; xs.append(x); ys.append(y); zs.append(z)
            xs.append(None); ys.append(None); zs.append(None)
        return xs,ys,zs,pts
    x,y,z,pts=coords(0)
    fig=go.Figure(data=[go.Scatter3d(x=x,y=y,z=z,mode="lines",line=dict(color="#67e8f9",width=9),hoverinfo="skip",showlegend=False),
        go.Scatter3d(x=[v[0] for v in pts.values()],y=[v[1] for v in pts.values()],z=[v[2] for v in pts.values()],mode="markers",marker=dict(size=[12 if n=="head" else 7 for n in pts],color=["#f5c9a5" if n=="head" else "#a7f3d0" for n in pts],line=dict(color="#e0f2fe",width=1)),text=list(pts.keys()),hovertemplate="Joint: %{text}<extra></extra>",showlegend=False)])
    frames=[]
    for i in range(24):
        xx,yy,zz,pp=coords(i*2*math.pi/23)
        frames.append(go.Frame(data=[go.Scatter3d(x=xx,y=yy,z=zz),go.Scatter3d(x=[v[0] for v in pp.values()],y=[v[1] for v in pp.values()],z=[v[2] for v in pp.values()])],name=str(i)))
    fig.frames=frames
    fig.update_layout(height=560,margin=dict(l=0,r=0,t=10,b=0),paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(bgcolor="rgba(0,0,0,0)",xaxis=dict(visible=False,range=[-1.35,1.35]),yaxis=dict(visible=False,range=[-.8,.8]),zaxis=dict(visible=False,range=[0,3.7]),aspectmode="manual",aspectratio=dict(x=1,y=.65,z=1.4),camera=dict(eye=dict(x=1.5,y=1.8,z=1.1))),
        updatemenus=[dict(type="buttons",showactive=False,x=.02,y=.98,xanchor="left",yanchor="top",buttons=[dict(label="▶ Play motion",method="animate",args=[None,{"frame":{"duration":85,"redraw":True},"transition":{"duration":45},"fromcurrent":True}]),dict(label="Ⅱ Pause",method="animate",args=[[None],{"mode":"immediate","frame":{"duration":0,"redraw":False},"transition":{"duration":0}}])])],
        sliders=[dict(active=0,x=.12,y=.02,len=.8,currentvalue=dict(prefix="Motion phase "),steps=[dict(method="animate",args=[[str(i)],{"mode":"immediate","frame":{"duration":0,"redraw":True},"transition":{"duration":0}}],label=str(i+1)) for i in range(24)])])
    return fig


# --------------------------- Sidebar ---------------------------
st.sidebar.markdown("# 💪 FITAI PRO")
st.sidebar.caption("Made by Souvik Dey")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Workout Planner",
        "3D Trainer",
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
        '<div class="hero"><div class="eyebrow">Personal performance system · 3D edition</div><h1>FITAI PRO 3D</h1>'
        '<p>Plan smarter. Track consistency. Build healthy habits.</p>'
        '<p>Made by Souvik Dey · Interactive fitness dashboard</p></div>',
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
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Your 3D performance space")
        st.caption("Explore your training data in 3D, then open 3D Trainer for animated exercise previews.")
        st.plotly_chart(fitness_3d_scene(), use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
        st.markdown("**Motion lab:** select any major muscle group in the 3D Trainer page to play or pause its movement preview.")
    with right:
        st.subheader("Build your baseline")
        st.markdown("""
        **Your daily system**
        - 🏋️ Log movement you enjoy
        - 💧 Record water throughout the day
        - 🥗 Choose varied, regular meals
        - 🌙 Leave room for rest and recovery
        """)
        st.info("Consistency beats intensity. Start comfortably and build gradually.")
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

# --------------------------- 3D Trainer ---------------------------
elif page == "3D Trainer":
    st.markdown('<div class="hero"><div class="eyebrow">Motion lab · interactive exercise guide</div><h1>3D TRAINER STUDIO</h1><p>Explore a full-body articulated trainer and preview movement patterns for major muscle groups.</p></div>', unsafe_allow_html=True)
    muscle = st.selectbox("Choose a muscle group", list(MUSCLE_MOVES.keys()))
    move = MUSCLE_MOVES[muscle]
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader(f"Animated 3D preview · {muscle}")
        st.caption("Use ▶ Play motion, Ⅱ Pause, or the phase slider. Drag the figure to rotate; scroll to zoom.")
        st.plotly_chart(animated_trainer(muscle), use_container_width=True, config={"displaylogo":False,"scrollZoom":True})
    with right:
        st.subheader(move["exercise"])
        st.markdown(f"**Main muscles:** {move['primary']}")
        st.markdown(f"**Suggested starting volume:** {move['sets']} · {move['reps']}")
        st.markdown("#### Technique cue")
        st.info(move["tip"])
        st.markdown("#### Session checklist")
        st.write("1. Warm up with easy movement.\n2. Practise the movement slowly before adding resistance.\n3. Breathe continuously and take breaks.\n4. Stop if you feel pain, dizziness, or unusual symptoms.")
        if st.button("Log this movement", type="primary", use_container_width=True):
            execute("INSERT INTO workouts (workout_date, workout_name, duration_min, notes) VALUES (?, ?, ?, ?)", (date.today().isoformat(), f"{muscle}: {move['exercise']}", 10, "Logged from 3D Trainer Studio"))
            st.success("Movement added to your workout history as a 10-minute practice session.")
    st.divider()
    st.subheader("All muscle groups")
    cards = st.columns(3)
    for i, (group, info) in enumerate(MUSCLE_MOVES.items()):
        with cards[i % 3]:
            st.markdown(f"**{group}**")
            st.caption(info["exercise"])
            st.write(info["primary"])
    st.warning("These are simplified animated motion previews, not clinical anatomy models or recorded workout videos. Ask a qualified coach to check technique in person when learning unfamiliar movements.")

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
    st.title("🤖 FITAI PRO Coach")
    st.markdown("### Your built-in coach · No API key or paid AI billing needed")
    st.write("This version uses a local rule-based coach for general fitness education. It works on Streamlit Cloud without an OpenAI API key.")

    def coach_reply(question):
        q = question.lower()
        if any(word in q for word in ["pain", "injury", "injured", "dizzy", "faint", "chest"]):
            return ("Please stop the activity if you have pain, dizziness, chest discomfort, or unusual shortness of breath. "
                    "Tell a trusted adult and contact a qualified health professional; severe or sudden symptoms need urgent medical help. "
                    "I can't diagnose symptoms.")
        if any(word in q for word in ["workout", "exercise", "training", "routine", "gym", "beginner"]):
            return ("**A balanced starting session**\n\n1. Warm up with 5–10 minutes of easy movement.\n"
                    "2. Choose a few comfortable movements: squat-to-chair, wall push-ups, glute bridges, and bird-dogs.\n"
                    "3. Move with control and take breaks whenever needed.\n4. Finish with easy movement and recover before your next session.\n\n"
                    "Adjust to your experience and ability; good technique matters more than lifting heavier or doing more.")
        if any(word in q for word in ["food", "diet", "nutrition", "protein", "meal", "eat"]):
            return ("Aim for **variety and regular meals**: include grains or other carbohydrates, protein foods such as dal/beans, eggs, dairy, tofu or meat if you eat them, plus fruit and vegetables. "
                    "Choose portions that leave you comfortably satisfied. Avoid crash diets or cutting out whole food groups. A qualified dietitian can help with individual needs.")
        if any(word in q for word in ["water", "hydration", "drink"]):
            return ("Keep water available and drink regularly, especially in hot weather and around activity. Needs vary with weather, activity, age, and health, so don't treat one fixed number as right for everyone. Follow medical advice if you have fluid restrictions.")
        if any(word in q for word in ["rest", "sleep", "recovery", "sore", "tired"]):
            return ("Recovery is part of training. Alternate harder sessions with easier activity or rest, aim for a regular sleep schedule, and eat enough to support everyday activity. If fatigue or soreness is persistent or unusual, speak with a qualified health professional.")
        if any(word in q for word in ["weight", "lose weight", "gain weight", "body"]):
            return ("Health and fitness are about more than a number: energy, strength, endurance, mood, sleep, and consistency matter too. Avoid extreme diets or trying to change your body quickly. If you have concerns about growth, weight, or nutrition, talk with a trusted adult and a qualified health professional.")
        return ("I can help with general workout planning, recovery, hydration, and balanced meals. Try asking: **'Give me a beginner workout'**, **'What is good recovery?'**, or **'How can I stay hydrated?'**\n\n"
                "I'm a simple built-in coach, not a clinician, and I can't diagnose medical issues.")

    if "offline_coach_history" not in st.session_state:
        st.session_state.offline_coach_history = []
    for item in st.session_state.offline_coach_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    question = st.chat_input("Ask about workouts, food, hydration, or recovery...")
    if question:
        st.session_state.offline_coach_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        answer = coach_reply(question)
        st.session_state.offline_coach_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    if st.button("Clear conversation"):
        st.session_state.offline_coach_history = []
        st.rerun()
    st.caption("Fitness education only; not medical advice. The built-in coach works without live AI or API billing.")

# --------------------------- Footer ---------------------------
st.divider()
st.caption(f"FITAI PRO · Made by Souvik Dey · {datetime.now().year}")
