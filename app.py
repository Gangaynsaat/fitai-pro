import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="FITAI PRO | 3D Muscle Trainer", page_icon="💪", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 15% 0%, #142235 0, #080d17 45%, #060910 100%); color:#edf5ff}
[data-testid="stSidebar"] {background:#0b1320}
h1,h2,h3,p,label {color:#edf5ff}
div[data-testid="stMetric"] {background:#101c2b;border:1px solid #22354a;padding:14px;border-radius:14px}
</style>
""", unsafe_allow_html=True)

st.title("FITAI PRO")
st.caption("3D MUSCLE TRAINER • Made by Souvik Dey")
st.markdown("Choose a muscle group to highlight it **blue** on the muscular 3D figure. Rotate the model and use the view buttons to inspect it.")

groups = {
    "Chest": ("Pectoralis major", "Push-up", "3 × 8–12", "Keep your body in a straight line; lower only as far as comfortable."),
    "Back": ("Latissimus dorsi + trapezius", "Bent-over row (light resistance)", "3 × 8–12", "Keep your spine neutral and move in a controlled way."),
    "Shoulders": ("Deltoids", "Shoulder press (light load)", "2–3 × 8–12", "Use a comfortable range; stop if you feel pain."),
    "Biceps": ("Biceps brachii", "Biceps curl", "2–3 × 10–12", "Keep elbows near your sides and avoid swinging."),
    "Triceps": ("Triceps brachii", "Triceps extension", "2–3 × 10–12", "Use light resistance and keep movement controlled."),
    "Abs / Core": ("Rectus abdominis + obliques", "Dead bug", "2–3 × 8 each side", "Keep your lower back comfortable and breathe normally."),
    "Glutes": ("Gluteus maximus", "Glute bridge", "2–3 × 10–15", "Lift smoothly without over-arching your back."),
    "Quads": ("Quadriceps", "Bodyweight squat", "2–3 × 8–12", "Keep feet stable and use a comfortable depth."),
    "Hamstrings": ("Hamstrings", "Hip hinge drill", "2–3 × 8–12", "Push hips back while keeping your back neutral."),
    "Calves": ("Gastrocnemius + soleus", "Calf raise", "2–3 × 12–15", "Use support for balance and move slowly.")
}
initial = st.query_params.get("muscle", "Chest")
if initial not in groups: initial = "Chest"
selected = st.selectbox("Target muscle group", list(groups.keys()), index=list(groups.keys()).index(initial))
info = groups[selected]
col1, col2 = st.columns([1.5, 1])
with col1:
    st.subheader("Interactive muscular figure")
    st.caption("Blue = selected target • Drag to rotate • Scroll/pinch to zoom")
    # Build self-contained Three.js viewer using CDN ESM. Procedural stylized muscular figure with separately selectable muscle forms.
    html = r"""
<div id="fitai3d" style="width:100%;height:540px;position:relative;background:linear-gradient(145deg,#0b1523,#111e2d);border:1px solid #24384d;border-radius:18px;overflow:hidden">
 <div id="loadmsg" style="position:absolute;top:12px;left:14px;z-index:2;color:#c8d8e9;font:12px sans-serif">Loading 3D trainer…</div>
 <div style="position:absolute;bottom:12px;left:14px;z-index:2;color:#9fb4ca;font:12px sans-serif">FITAI PRO • MUSCLE MAP</div>
</div>
<script type="module">
const root=document.getElementById('fitai3d');
try {
 const THREE=await import('https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js/+esm');
 const {OrbitControls}=await import('https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/OrbitControls.js/+esm');
 const scene=new THREE.Scene(); scene.background=new THREE.Color('#0b1523');
 const camera=new THREE.PerspectiveCamera(35,root.clientWidth/root.clientHeight,.1,100); camera.position.set(0,1.8,8.6);
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false}); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(root.clientWidth,root.clientHeight); renderer.outputColorSpace=THREE.SRGBColorSpace; root.appendChild(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement); controls.target.set(0,1.5,0); controls.enableDamping=true; controls.minDistance=5; controls.maxDistance=12;
 scene.add(new THREE.HemisphereLight(0xc6e5ff,0x18202d,2.1));
 const key=new THREE.DirectionalLight(0xffffff,3); key.position.set(4,6,5); scene.add(key);
 const rim=new THREE.PointLight(0x1c8fff,35); rim.position.set(-3,3,2); scene.add(rim);
 const floor=new THREE.Mesh(new THREE.CircleGeometry(2.5,64),new THREE.MeshStandardMaterial({color:0x152538,roughness:.9})); floor.rotation.x=-Math.PI/2; floor.position.y=-.03; scene.add(floor);
 const mats={base:new THREE.MeshStandardMaterial({color:0xb86f58,roughness:.62,metalness:.02}), muscle:new THREE.MeshStandardMaterial({color:0xa84f43,roughness:.48}), blue:new THREE.MeshStandardMaterial({color:0x159cff,emissive:0x0068ff,emissiveIntensity:.65,roughness:.35}), dark:new THREE.MeshStandardMaterial({color:0x5b302e,roughness:.7})};
 const parts={}; const group=new THREE.Group(); scene.add(group);
 function ell(name,x,y,z,sx,sy,sz,category,rot=0,material='muscle'){
  const m=new THREE.Mesh(new THREE.SphereGeometry(1,24,18),mats[material]); m.position.set(x,y,z); m.scale.set(sx,sy,sz); m.rotation.z=rot; m.userData={category,name,normalMaterial:mats[material]}; group.add(m); (parts[category]??=[]).push(m); return m;
 }
 function limb(name,a,b,r1,r2,cat,mat='muscle'){
  const va=new THREE.Vector3(...a), vb=new THREE.Vector3(...b), d=new THREE.Vector3().subVectors(vb,va);
  const mesh=new THREE.Mesh(new THREE.CylinderGeometry(r2,r1,d.length(),18,1),mats[mat]); mesh.position.copy(va).add(vb).multiplyScalar(.5); mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize()); mesh.userData={category:cat,name,normalMaterial:mats[mat]}; group.add(mesh); (parts[cat]??=[]).push(mesh); return mesh;
 }
 // head, neck, torso
 ell('Head',0,3.55,0,.37,.46,.32,'Other','0','base');
 ell('Neck',0,3.03,0,.19,.27,.19,'Other',0,'base');
 ell('Upper chest',0,2.55,0,.72,.49,.3,'Chest');
 ell('Lower torso',0,1.95,0,.51,.55,.27,'Abs / Core');
 ell('Pelvis',0,1.39,0,.48,.28,.28,'Glutes');
 // chest pectorals, abdominal segments
 ell('Left pectoral',-.34,2.62,.255,.37,.27,.12,'Chest',-.12);
 ell('Right pectoral',.34,2.62,.255,.37,.27,.12,'Chest',.12);
 for(let i=0;i<3;i++){ell('Left abdominal segment',-.14,2.23-i*.18,.245,.12,.075,.045,'Abs / Core');ell('Right abdominal segment',.14,2.23-i*.18,.245,.12,.075,.045,'Abs / Core');}
 ell('Left oblique',-.39,2.0,.17,.12,.31,.1,'Abs / Core',-.24); ell('Right oblique',.39,2.0,.17,.12,.31,.1,'Abs / Core',.24);
 // back layers
 ell('Left latissimus',-.34,2.32,-.22,.31,.42,.13,'Back',-.18); ell('Right latissimus',.34,2.32,-.22,.31,.42,.13,'Back',.18);
 ell('Trapezius',0,2.76,-.22,.36,.31,.12,'Back');
 // deltoids and arms both sides
 for(const s of [-1,1]){
  ell('Deltoid',s*.76,2.72,0,.24,.27,.23,'Shoulders',s*.15);
  limb('Upper arm', [s*.82,2.55,0],[s*1.0,1.92,0],.16,.12,'Biceps','base');
  ell('Biceps brachii',s*.91,2.27,.13,.13,.29,.13,'Biceps',s*.15);
  ell('Triceps brachii',s*.92,2.25,-.12,.12,.29,.1,'Triceps',-s*.15);
  limb('Forearm',[s*1.0,1.93,0],[s*1.1,1.34,.03],.12,.085,'Forearms','base');
  ell('Hand',s*1.11,1.25,.03,.11,.17,.08,'Forearms',0,'base');
  // legs
  limb('Thigh', [s*.27,1.36,0],[s*.34,.65,0],.22,.15,'Quads','base');
  ell('Quadriceps muscle',s*.32,1.0,.13,.17,.37,.13,'Quads',-s*.06);
  ell('Hamstrings muscle',s*.32,1.0,-.13,.15,.36,.1,'Hamstrings',s*.06);
  ell('Glute muscle',s*.29,1.43,-.12,.23,.24,.14,'Glutes');
  limb('Shin',[s*.34,.64,0],[s*.34,.12,.02],.13,.085,'Calves','base');
  ell('Calf muscle',s*.35,.42,-.10,.13,.24,.12,'Calves');
  ell('Foot',s*.34,.07,.14,.14,.08,.25,'Other',0,'base');
 }
 // subtle muscle lines
 for(const s of [-1,1]) {
  ell('Shoulder cap',s*.76,2.76,.13,.18,.18,.12,'Shoulders');
 }
 function highlight(cat){
  for(const [key,arr] of Object.entries(parts)) for(const m of arr) m.material=(key===cat)?mats.blue:m.userData.normalMaterial;
 }
 highlight('Chest');
 window.fitaiSelectMuscle=highlight;
 const observer=new ResizeObserver(()=>{camera.aspect=root.clientWidth/root.clientHeight;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,root.clientHeight);}); observer.observe(root);
 document.getElementById('loadmsg').textContent='Drag to rotate • scroll to zoom';
 function animate(t){requestAnimationFrame(animate); group.position.y=Math.sin(t*.0012)*.025; controls.update(); renderer.render(scene,camera);}
 animate(0);
} catch(e){document.getElementById('loadmsg').textContent='3D viewer could not load. Check your internet connection and WebGL support.'; console.error(e);}
</script>
"""
    # Replace default highlighted category based on selected group, safely as JS string
    html = html.replace("highlight('Chest');", "highlight(" + json.dumps(selected) + ");")
    components.html(html, height=560, scrolling=False)
with col2:
    st.subheader(f"🎯 {selected}")
    st.markdown(f"**Main muscles:** {info[0]}")
    st.markdown(f"**Exercise:** {info[1]}")
    st.markdown(f"**Beginner guide:** {info[2]}")
    st.info(info[3])
    st.markdown("### Muscle groups")
    selected2 = st.radio("Select a group to highlight", list(groups.keys()), index=list(groups.keys()).index(selected), label_visibility="collapsed")
    if selected2 != selected:
        st.query_params["muscle"] = selected2
        st.rerun()
    st.markdown("---")
    st.metric("Target selected", selected)
    st.caption("The blue highlight identifies the selected muscle-group region in this stylized educational model. It is not a medical-grade anatomical model.")

st.markdown("---")
st.subheader("How to use")
st.write("1. Select a muscle group. 2. The corresponding region is highlighted blue. 3. Drag the 3D figure to rotate and use the scroll wheel to zoom. 4. Follow the technique guidance and choose a comfortable starting level.")
st.caption("Safety: warm up first, use controlled movements, and stop if an exercise causes pain. Ask a qualified coach for help with technique.")
