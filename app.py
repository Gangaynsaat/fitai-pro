import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "fitai_pro.db"

st.set_page_config(
    page_title="FITAI PRO 3D | Made by Souvik Dey",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)


def accurate_motion_viewer(muscle, exercise):
    """Embedded articulated trainer. Motion is a simplified teaching animation, not medical-grade motion capture."""
    import json
    muscle_json = json.dumps(muscle)
    exercise_json = json.dumps(exercise)
    html = r"""
<div id="fitai-motion" style="height:610px;width:100%;border-radius:18px;overflow:hidden;background:#081321;border:1px solid #243b50;position:relative">
 <div id="fitai-status" style="position:absolute;top:12px;left:14px;z-index:5;color:#d9e9f7;font:13px system-ui">Preparing 3D trainer…</div>
 <div style="position:absolute;bottom:12px;left:14px;right:14px;display:flex;gap:8px;flex-wrap:wrap;z-index:5">
  <button id="fitai-play" style="padding:9px 14px;border:0;border-radius:9px;background:#159cff;color:#fff;font-weight:700;cursor:pointer">Ⅱ Pause</button>
  <button id="fitai-reset" style="padding:9px 14px;border:1px solid #47627b;border-radius:9px;background:#14273a;color:#fff;cursor:pointer">↺ Reset</button>
  <label style="color:#d9e9f7;display:flex;align-items:center;gap:8px;font:12px system-ui">Speed <select id="fitai-speed" style="padding:7px;background:#14273a;color:#fff;border:1px solid #47627b;border-radius:8px"><option value=".65">Slow</option><option value="1" selected>Normal</option><option value="1.25">Fast</option></select></label>
 </div>
</div>
<script type="module">
const root=document.getElementById('fitai-motion');
const muscle=__MUSCLE__;
const exercise=__EXERCISE__;
try {
 const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js/+esm');
 const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/OrbitControls.js/+esm');
 const scene=new THREE.Scene(); scene.background=new THREE.Color('#081321');
 const camera=new THREE.PerspectiveCamera(35,root.clientWidth/root.clientHeight,.1,100); camera.position.set(0,1.8,7.8);
 const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(root.clientWidth,root.clientHeight); renderer.outputColorSpace=THREE.SRGBColorSpace; root.appendChild(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement); controls.target.set(0,1.45,0); controls.enableDamping=true; controls.minDistance=5; controls.maxDistance=11;
 scene.add(new THREE.HemisphereLight(0xcce8ff,0x241a1b,2.0));
 const light=new THREE.DirectionalLight(0xffffff,2.7); light.position.set(3,5,5); scene.add(light);
 const blueLight=new THREE.PointLight(0x159cff,28); blueLight.position.set(-3,2,2); scene.add(blueLight);
 const floor=new THREE.Mesh(new THREE.CircleGeometry(2.6,64),new THREE.MeshStandardMaterial({color:0x13283b,roughness:.9})); floor.rotation.x=-Math.PI/2; floor.position.y=-.04; scene.add(floor);
 const skin=new THREE.MeshStandardMaterial({color:0xb97860,roughness:.56});
 const muscleMat=new THREE.MeshStandardMaterial({color:0x9e453e,roughness:.48});
 const activeMat=new THREE.MeshStandardMaterial({color:0x159cff,emissive:0x006cff,emissiveIntensity:.55,roughness:.35});
 const dark=new THREE.MeshStandardMaterial({color:0x2b3e52,roughness:.65});
 const model=new THREE.Group(); scene.add(model);
 function sphere(parent,name,pos,scale,mat,active=false){const m=new THREE.Mesh(new THREE.SphereGeometry(1,24,18),mat);m.name=name;m.position.set(...pos);m.scale.set(...scale);m.userData.active=active;parent.add(m);return m;}
 function bone(parent,name,a,b,r1,r2,mat){const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),d=vb.clone().sub(va);const m=new THREE.Mesh(new THREE.CylinderGeometry(r2,r1,d.length(),16),mat);m.name=name;m.position.copy(va).add(vb).multiplyScalar(.5);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());parent.add(m);m.userData.a=new THREE.Vector3(...a);m.userData.b=new THREE.Vector3(...b);m.userData.r1=r1;m.userData.r2=r2;return m;}
 // articulated pivots are used so joint motion is visible, with muscle volumes attached to body segments
 const pelvis=new THREE.Group(); pelvis.position.set(0,1.25,0);model.add(pelvis);
 sphere(pelvis,'pelvis',[0,0,0],[.42,.25,.26],skin);
 const torso=new THREE.Group(); torso.position.set(0,.18,0);pelvis.add(torso);
 sphere(torso,'abdominal wall',[0,.35,0],[.43,.53,.25],muscleMat);
 sphere(torso,'left pec',[-.23,.72,.18],[.26,.22,.12],muscleMat,muscle==='Chest');
 sphere(torso,'right pec',[.23,.72,.18],[.26,.22,.12],muscleMat,muscle==='Chest');
 for(let i=0;i<3;i++){sphere(torso,'left abs',[-.105,.43-i*.15,.22],[.095,.065,.04],muscleMat,muscle==='Abs / Core');sphere(torso,'right abs',[.105,.43-i*.15,.22],[.095,.065,.04],muscleMat,muscle==='Abs / Core');}
 sphere(torso,'left lat',[-.34,.48,-.15],[.18,.38,.12],muscleMat,muscle==='Back');sphere(torso,'right lat',[.34,.48,-.15],[.18,.38,.12],muscleMat,muscle==='Back');
 sphere(torso,'neck',[0,.93,0],[.14,.19,.14],skin);sphere(torso,'head',[0,1.22,0],[.27,.34,.25],skin);
 const shoulders=[],elbows=[],hips=[],knees=[],ankles=[],arms=[],forearms=[],thighs=[],shins=[],hands=[],feet=[],delts=[],biceps=[],triceps=[],quads=[],hams=[],calves=[];
 for(const s of [-1,1]){
  const sh=new THREE.Group();sh.position.set(s*.49,.76,0);torso.add(sh); shoulders.push({s,p:sh});
  sphere(sh,'deltoid',[0,0,0],[.2,.22,.2],muscleMat,muscle==='Shoulders');
  const upper=sphere(sh,'upper arm',[s*.02,-.29,0],[.13,.3,.13],skin);
  sphere(sh,'biceps',[s*.015,-.29,.105],[.105,.22,.075],muscleMat,muscle==='Biceps');
  sphere(sh,'triceps',[s*.015,-.29,-.09],[.1,.22,.065],muscleMat,muscle==='Triceps');
  const elbow=new THREE.Group();elbow.position.set(0,-.55,0);sh.add(elbow);elbows.push({s,p:elbow});
  sphere(elbow,'elbow',[0,0,0],[.105,.11,.105],skin);
  sphere(elbow,'forearm',[0,-.25,.015],[.095,.27,.095],skin);
  sphere(elbow,'hand',[0,-.51,.04],[.09,.12,.055],skin);hands.push({s,p:elbow});
  const hip=new THREE.Group();hip.position.set(s*.22,-.08,0);pelvis.add(hip);hips.push({s,p:hip});
  sphere(hip,'quad',[0,-.34,.105],[.16,.37,.13],muscleMat,muscle==='Quads');
  sphere(hip,'hamstring',[0,-.34,-.095],[.14,.36,.1],muscleMat,muscle==='Hamstrings');
  const knee=new THREE.Group();knee.position.set(0,-.67,0);hip.add(knee);knees.push({s,p:knee});
  sphere(knee,'knee',[0,0,0],[.12,.12,.12],skin);
  sphere(knee,'calf',[0,-.28,-.075],[.12,.28,.11],muscleMat,muscle==='Calves');
  sphere(knee,'shin',[0,-.27,.01],[.085,.29,.085],skin);
  sphere(knee,'foot',[0,-.56,.12],[.12,.08,.23],skin);
 }
 // target regions blue, while other anatomy remains warm-toned
 model.traverse(o=>{if(o.isMesh && (o.name.toLowerCase().includes('pec') && muscle==='Chest' || o.name.toLowerCase().includes('abs') && muscle==='Abs / Core' || o.name.toLowerCase().includes('lat') && muscle==='Back' || o.name==='deltoid' && muscle==='Shoulders' || o.name==='biceps' && muscle==='Biceps' || o.name==='triceps' && muscle==='Triceps' || o.name==='quad' && muscle==='Quads' || o.name==='hamstring' && muscle==='Hamstrings' || o.name==='calf' && muscle==='Calves')) o.material=activeMat;});
 // movement presets: each animation changes joint angles through a repeatable controlled range.
 // Squat: hips/knees flex together; curl: elbows flex; push-up: torso lowers while elbows flex.
 let playing=true,phase=0,speed=1,last=performance.now();
 function motion(t){
  const flex=(1-Math.cos(t*2*Math.PI))/2;
  const ex=exercise.toLowerCase();
  // Restore neutral pose each frame to avoid accumulating joint rotation.
  model.rotation.set(0,0,0); model.position.set(0,0,0);
  torso.rotation.set(0,0,0); pelvis.rotation.set(0,0,0); pelvis.position.set(0,1.25,0);
  shoulders.forEach(({p})=>p.rotation.set(0,0,0));
  elbows.forEach(({p})=>p.rotation.set(0,0,0));
  hips.forEach(({p})=>p.rotation.set(0,0,0));
  knees.forEach(({p})=>p.rotation.set(0,0,0));
  // Each family is a teaching approximation; exercise names select the closest movement pattern.
  if(ex.includes('push-up') || ex.includes('push up') || ex.includes('pushup') || ex.includes('bench press') || ex.includes('chest press')){
    // Rotate the full body into a prone plank: head/chest at one end, legs at the other.
    model.rotation.z=-Math.PI/2; model.position.set(-.05,1.30,0);
    // Elbows flex on the lowering phase; chest moves toward the floor and returns as one unit.
    elbows.forEach(({p})=>{p.rotation.z=-(.08+flex*.95);});
    shoulders.forEach(({s,p})=>{p.rotation.z=s*.02;});
    pelvis.position.y=1.25-flex*.035; torso.rotation.z=flex*.015;
  } else if(ex.includes('squat') || ex.includes('lunge') || ex.includes('leg press')){
    const bend=flex*(ex.includes('lunge')?0.72:0.95);
    hips.forEach(({p,s})=>{p.rotation.z=s*(-bend*.18);});
    knees.forEach(({p})=>{p.rotation.z=-bend*.88;});
    pelvis.position.y=1.25-flex*.22; torso.rotation.z=-flex*.12;
  } else if(ex.includes('deadlift') || ex.includes('romanian') || ex.includes('good morning') || ex.includes('hip hinge')){
    hips.forEach(({p,s})=>{p.rotation.z=s*(-flex*.16);});
    knees.forEach(({p})=>{p.rotation.z=-flex*.20;});
    torso.rotation.z=-flex*.42; pelvis.position.y=1.25-flex*.04;
    elbows.forEach(({p})=>{p.rotation.z=-.05;});
  } else if(ex.includes('bridge') || ex.includes('hip thrust')){
    pelvis.position.y=1.25+flex*.18; torso.rotation.z=flex*.12;
    knees.forEach(({p})=>{p.rotation.z=-.5;});
  } else if(ex.includes('curl') || ex.includes('chin-up') || ex.includes('chin up')){
    elbows.forEach(({p})=>{p.rotation.z=-flex*1.12;});
    shoulders.forEach(({s,p})=>{p.rotation.z=s*(ex.includes('chin')?-.2:.03);});
  } else if(ex.includes('row') || ex.includes('pulldown') || ex.includes('pull-up') || ex.includes('pull up')){
    torso.rotation.z=ex.includes('row')?-.18:0;
    shoulders.forEach(({s,p})=>{p.rotation.z=s*(.12-flex*.36);});
    elbows.forEach(({p})=>{p.rotation.z=-flex*.82;});
  } else if(ex.includes('overhead press') || ex.includes('shoulder press') || ex.includes('lateral raise') || ex.includes('front raise') || ex.includes('fly') || ex.includes('pullover')){
    const raise=ex.includes('raise')||ex.includes('fly');
    shoulders.forEach(({s,p})=>{p.rotation.z=s*(raise?flex*.82:-flex*.78);});
    elbows.forEach(({p})=>{p.rotation.z=ex.includes('fly')?-.22:-(ex.includes('press')?.18:0);});
  } else if(ex.includes('triceps') || ex.includes('pushdown') || ex.includes('skull crusher')){
    shoulders.forEach(({p})=>{p.rotation.z=-.18;});
    elbows.forEach(({p})=>{p.rotation.z=-(.12+flex*.62);});
  } else if(ex.includes('crunch') || ex.includes('sit-up') || ex.includes('sit up') || ex.includes('dead bug') || ex.includes('leg raise') || ex.includes('plank')){
    torso.rotation.z=flex*.20;
    hips.forEach(({p})=>{p.rotation.z=ex.includes('leg raise')||ex.includes('dead bug')?flex*.45:0;});
    knees.forEach(({p})=>{p.rotation.z=ex.includes('dead bug')?-flex*.55:0;});
  } else if(ex.includes('calf')){
    model.position.y=Math.sin(t*2*Math.PI)*.06;
  } else {
    // General controlled accessory movement; avoid exaggerated full-body swinging.
    elbows.forEach(({p})=>{p.rotation.z=-flex*.38;});
    shoulders.forEach(({p})=>{p.rotation.z=-flex*.12;});
  }
 }
 function loop(now){requestAnimationFrame(loop);const dt=Math.min((now-last)/1000,.05);last=now;if(playing)phase+=dt*speed;motion(phase);controls.update();renderer.render(scene,camera);}
 requestAnimationFrame(loop);
 document.getElementById('fitai-status').textContent='3D muscular trainer • drag to rotate • scroll to zoom';
 document.getElementById('fitai-play').addEventListener('click',e=>{playing=!playing;e.currentTarget.textContent=playing?'Ⅱ Pause':'▶ Play';});
 document.getElementById('fitai-reset').addEventListener('click',()=>{phase=0;model.position.set(0,0,0);model.rotation.set(0,0,0);});
 document.getElementById('fitai-speed').addEventListener('change',e=>speed=Number(e.target.value)||1);
 const ro=new ResizeObserver(()=>{camera.aspect=root.clientWidth/root.clientHeight;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,root.clientHeight);});ro.observe(root);
} catch(err){document.getElementById('fitai-status').textContent='3D trainer could not load. Check internet connection and WebGL support.';console.error(err);}
</script>
"""
    html = html.replace("__MUSCLE__", muscle_json).replace("__EXERCISE__", exercise_json)
    components.html(html, height=625, scrolling=False)


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
EXERCISES = {
    "Bodyweight": {
        "Chest": ["Push-up", "Incline push-up", "Knee push-up", "Decline push-up", "Wide-grip push-up", "Close-grip push-up", "Pike push-up"],
        "Back": ["Superman raise", "Bird dog", "Inverted row", "Pull-up", "Chin-up", "Scapular pull-up"],
        "Shoulders": ["Pike push-up", "Arm circles", "Wall slide", "Plank shoulder tap"],
        "Biceps": ["Chin-up", "Inverted row"],
        "Triceps": ["Close-grip push-up", "Bench dip", "Diamond push-up"],
        "Legs / Quads": ["Bodyweight squat", "Reverse lunge", "Forward lunge", "Split squat", "Step-up", "Wall sit", "Jump squat"],
        "Glutes": ["Glute bridge", "Single-leg glute bridge", "Hip thrust", "Donkey kick", "Fire hydrant"],
        "Hamstrings": ["Glute bridge", "Single-leg glute bridge", "Hip hinge", "Nordic curl"],
        "Core / Abs": ["Plank", "Side plank", "Crunch", "Bicycle crunch", "Reverse crunch", "Leg raise", "Dead bug", "Mountain climber"],
        "Calves": ["Standing calf raise", "Single-leg calf raise"],
        "Full body": ["Burpee", "Bear crawl", "Mountain climber", "Bodyweight squat"]
    },
    "Dumbbell": {
        "Chest": ["Dumbbell bench press", "Dumbbell incline press", "Dumbbell floor press", "Dumbbell chest fly", "Dumbbell squeeze press", "Dumbbell pullover"],
        "Back": ["One-arm dumbbell row", "Chest-supported dumbbell row", "Dumbbell bent-over row", "Dumbbell reverse fly", "Dumbbell pullover", "Dumbbell shrug"],
        "Shoulders": ["Dumbbell shoulder press", "Seated dumbbell press", "Dumbbell lateral raise", "Dumbbell front raise", "Dumbbell rear-delt fly", "Arnold press"],
        "Biceps": ["Dumbbell biceps curl", "Hammer curl", "Incline dumbbell curl", "Concentration curl", "Alternating dumbbell curl", "Zottman curl"],
        "Triceps": ["Overhead dumbbell triceps extension", "Dumbbell kickback", "Dumbbell skull crusher", "Close-grip dumbbell press"],
        "Legs / Quads": ["Goblet squat", "Dumbbell split squat", "Dumbbell reverse lunge", "Dumbbell step-up", "Dumbbell walking lunge"],
        "Glutes": ["Dumbbell hip thrust", "Dumbbell Romanian deadlift", "Dumbbell reverse lunge", "Dumbbell sumo squat"],
        "Hamstrings": ["Dumbbell Romanian deadlift", "Dumbbell single-leg deadlift", "Dumbbell good morning"],
        "Core / Abs": ["Dumbbell Russian twist", "Dumbbell sit-up", "Dumbbell side bend", "Dumbbell wood chop"],
        "Calves": ["Dumbbell standing calf raise", "Dumbbell seated calf raise"],
        "Full body": ["Dumbbell thruster", "Dumbbell clean and press", "Dumbbell farmer carry"]
    },
    "Barbell": {
        "Chest": ["Barbell bench press", "Barbell incline bench press", "Barbell close-grip bench press", "Barbell floor press"],
        "Back": ["Barbell bent-over row", "Pendlay row", "Barbell shrug", "Barbell rack pull"],
        "Shoulders": ["Barbell overhead press", "Push press", "Behind-the-neck press (advanced; avoid if uncomfortable)"],
        "Biceps": ["Barbell curl", "EZ-bar curl", "Reverse barbell curl"],
        "Triceps": ["Close-grip barbell bench press", "EZ-bar skull crusher", "Barbell lying triceps extension"],
        "Legs / Quads": ["Barbell back squat", "Barbell front squat", "Barbell box squat", "Barbell split squat"],
        "Glutes": ["Barbell hip thrust", "Barbell squat", "Barbell sumo deadlift"],
        "Hamstrings": ["Barbell Romanian deadlift", "Barbell deadlift", "Good morning"],
        "Core / Abs": ["Barbell rollout", "Landmine rotation"],
        "Calves": ["Barbell standing calf raise"],
        "Full body": ["Barbell deadlift", "Barbell clean pull", "Barbell thruster"]
    },
    "Cable / Machine": {
        "Chest": ["Cable chest fly", "Cable crossover", "Standing cable chest press", "Low-to-high cable fly", "High-to-low cable fly"],
        "Back": ["Lat pulldown", "Seated cable row", "Straight-arm cable pulldown", "Single-arm cable row", "Face pull"],
        "Shoulders": ["Cable lateral raise", "Cable front raise", "Cable rear-delt fly", "Cable upright row", "Face pull"],
        "Biceps": ["Cable biceps curl", "Rope hammer curl", "High cable curl", "Single-arm cable curl"],
        "Triceps": ["Cable triceps pushdown", "Rope pushdown", "Overhead cable triceps extension", "Single-arm cable extension"],
        "Legs / Quads": ["Leg press", "Leg extension", "Cable squat"],
        "Glutes": ["Cable kickback", "Cable pull-through", "Hip abduction machine"],
        "Hamstrings": ["Seated leg curl", "Lying leg curl", "Cable pull-through"],
        "Core / Abs": ["Cable crunch", "Pallof press", "Cable wood chop", "Cable rotation"],
        "Calves": ["Seated calf raise", "Standing calf raise machine"],
        "Full body": ["Cable squat to row", "Cable lift", "Sled push"]
    }
}

EXERCISE_INFO = {
    "Push-up": ("Chest, triceps, front shoulders and trunk", "2–3 sets", "6–12 controlled reps", "Keep ears, shoulders, hips and ankles in one line. Lower the chest between the hands; elbows travel diagonally back, then press the floor away."),
    "Incline push-up": ("Chest, triceps and shoulders", "2–3 sets", "6–12 controlled reps", "Use a stable bench or wall, keep the body straight and lower the chest toward the support."),
    "Dumbbell bench press": ("Chest, triceps and front shoulders", "2–3 sets", "8–12 controlled reps", "Use a stable bench and manageable weights. Lower with control; a spotter is sensible for challenging loads."),
    "Barbell bench press": ("Chest, triceps and front shoulders", "2–3 sets", "6–10 controlled reps", "Use safety arms or a competent spotter. Keep wrists stacked and lower under control; do not test maximal loads alone."),
    "Lat pulldown": ("Lats, upper back and biceps", "2–3 sets", "8–12 controlled reps", "Pull the bar toward the upper chest without swinging or pulling behind the neck."),
    "Barbell deadlift": ("Glutes, hamstrings, back and trunk", "2–3 technique sets", "5–8 controlled reps", "Learn the hip hinge with a coach and light load first. Keep the bar close and stop if you feel pain."),
    "Bodyweight squat": ("Quadriceps, glutes and trunk", "2–3 sets", "8–12 controlled reps", "Keep feet planted, knees tracking in line with toes, and use a comfortable depth."),
    "Dumbbell biceps curl": ("Biceps and forearms", "2 sets", "8–12 controlled reps", "Keep elbows near your sides and avoid swinging the torso."),
    "Cable triceps pushdown": ("Triceps", "2 sets", "10–15 controlled reps", "Keep elbows close to your sides and move the forearms smoothly."),
}
DEFAULT_INFO = ("Target muscles and supporting stabilisers", "2 comfortable sets", "8–12 controlled reps", "Start with a light or manageable resistance, practise the movement slowly, and use a pain-free range. Ask a qualified coach to check unfamiliar weighted exercises.")



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
    st.markdown('<div class="hero"><div class="eyebrow">Motion lab · bodyweight + resistance training</div><h1>3D TRAINER STUDIO</h1><p>Choose an exercise family, target muscle and movement. Preview the movement and review technique cues.</p></div>', unsafe_allow_html=True)
    family = st.selectbox("Equipment / exercise family", list(EXERCISES.keys()), index=0)
    muscle = st.selectbox("Target muscle group", list(EXERCISES[family].keys()))
    exercise = st.selectbox("Choose exercise", EXERCISES[family][muscle])
    primary, sets, reps, tip = EXERCISE_INFO.get(exercise, DEFAULT_INFO)
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader(f"Muscular 3D figure · {muscle}")
        st.caption("Blue highlights the selected target region. Drag to rotate; scroll to zoom; use the controls to pause, reset or adjust speed.")
        accurate_motion_viewer(muscle, exercise)
    with right:
        st.subheader(exercise)
        st.markdown(f"**Equipment:** {family}")
        st.markdown(f"**Main muscles:** {primary}")
        st.markdown(f"**Suggested practice:** {sets} · {reps}")
        st.markdown("#### Technique cue")
        st.info(tip)
        st.markdown("#### Safety and form")
        st.write("Warm up first, begin with manageable resistance, and prioritise controlled technique over load. Use a qualified coach or spotter for unfamiliar or challenging barbell lifts. Stop if you feel pain, dizziness or unusual shortness of breath.")
        if st.button("Log this movement", type="primary", use_container_width=True):
            execute("INSERT INTO workouts (workout_date, workout_name, duration_min, notes) VALUES (?, ?, ?, ?)", (date.today().isoformat(), f"{family} · {muscle}: {exercise}", 10, "Logged from 3D Trainer Studio"))
            st.success("Movement added to your workout history.")
    st.caption("Important: the 3D motion is a procedural educational approximation, not motion-capture-verified biomechanics. The library is broad, but the current mannequin does not yet render a distinct physical prop for every dumbbell, barbell or cable exercise. Use coaching and reference demonstrations for exact setup and form.")

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
