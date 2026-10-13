import math
import time

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Flywheel Lab Simulator", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #08111f 0%, #101d31 55%, #101827 100%); color: #eef4ff; }
    h1, h2, h3 { color: #f4f8ff !important; }
    [data-testid="stMetric"] { background: rgba(255,255,255,.055); border: 1px solid rgba(130,170,220,.2); padding: 14px; border-radius: 14px; }
    .hero { padding: 1.2rem 1.4rem; border: 1px solid rgba(130,170,220,.25); border-radius: 18px; background: linear-gradient(120deg,rgba(35,72,117,.55),rgba(20,31,51,.65)); margin-bottom: 1rem; }
    .muted { color: #a9bbd3; }
    div.stButton > button { border-radius: 10px; font-weight: 650; }
</style>
""", unsafe_allow_html=True)

G = 9.81

def flywheel_animation(mode, rpm, mass, radius, drop_height, inertia, friction_torque, run_key):
    # Canvas animation is rendered in the browser; it does not force Python reruns per frame.
    html = r"""
<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html,body{margin:0;padding:0;background:#08111f;font-family:system-ui,Arial;color:#eaf2ff;overflow:hidden}
.wrap{position:relative;width:100%;height:510px;background:radial-gradient(ellipse at 54% 42%,#172c47 0%,#0a1424 66%,#07101c 100%);border:1px solid #263d5c;border-radius:18px;overflow:hidden}
canvas{width:100%;height:100%;display:block}
.badge{position:absolute;left:16px;top:14px;background:#14243a;border:1px solid #304966;border-radius:10px;padding:8px 12px;font-size:12px;letter-spacing:.08em;color:#a9d9ff}
.hint{position:absolute;right:16px;bottom:12px;color:#9eb3ce;font-size:12px}
</style></head><body><div class="wrap"><div class="badge" id="badge">LIVE ROTATION · AUTOMATIC</div><canvas id="c"></canvas><div class="hint" id="hint">Canvas animation · physics-inspired visualization</div></div>
<script>
const canvas=document.getElementById('c'),ctx=canvas.getContext('2d');
const mode=__MODE__, targetRPM=__RPM__, m=__MASS__, r=__RADIUS__, h=__HEIGHT__, I=__INERTIA__, tau=__TAU__, runKey=__RUNKEY__;
let angle=0, last=0, elapsed=0, phase=mode==='experiment'?'ready':'demo', omega=targetRPM*2*Math.PI/60, initialOmega=omega;
const badge=document.getElementById('badge'), hint=document.getElementById('hint');
function resize(){const dpr=window.devicePixelRatio||1;canvas.width=canvas.clientWidth*dpr;canvas.height=canvas.clientHeight*dpr;ctx.setTransform(dpr,0,0,dpr,0,0)}
window.addEventListener('resize',resize);resize();
function line(x1,y1,x2,y2,color,w=2){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=w;ctx.stroke()}
function wheel(cx,cy,R,a){
  ctx.save();ctx.translate(cx,cy);
  // Outer rim and inner rings
  ctx.beginPath();ctx.arc(0,0,R,0,Math.PI*2);ctx.fillStyle='#14253b';ctx.fill();ctx.lineWidth=12;ctx.strokeStyle='#86a6c8';ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,R-12,0,Math.PI*2);ctx.lineWidth=2;ctx.strokeStyle='#314c6d';ctx.stroke();
  ctx.rotate(a);
  for(let i=0;i<8;i++){ctx.rotate(Math.PI/4);line(0,0,R-13,0,i%2?'#70c9ff':'#d7e8fa',5)}
  ctx.beginPath();ctx.arc(0,0,R*.63,0,Math.PI*2);ctx.strokeStyle='#456587';ctx.lineWidth=3;ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,12,0,Math.PI*2);ctx.fillStyle='#dbeeff';ctx.fill();ctx.strokeStyle='#5f8dbb';ctx.lineWidth=4;ctx.stroke();
  // Bright reference mark on rim
  ctx.beginPath();ctx.arc(R-7,0,7,0,Math.PI*2);ctx.fillStyle='#ffd166';ctx.fill();ctx.strokeStyle='#fff0bc';ctx.lineWidth=2;ctx.stroke();
  ctx.restore();
}
function draw(t){
  if(!last)last=t;let dt=Math.min((t-last)/1000,.04);last=t;elapsed+=dt;
  const W=canvas.clientWidth,H=canvas.clientHeight;ctx.clearRect(0,0,W,H);
  const cx=W*.58,cy=H*.48,R=Math.min(H*.31,W*.23);
  // floor / frame
  line(24,H*.83,W-24,H*.83,'#314760',3);
  line(cx,cy-R-45,cx,cy-R-15,'#8ba9c8',5);
  // support frame
  line(cx-R*.75,cy+R*.72,cx-R*.75,H*.82,'#4c6682',5);
  line(cx+R*.75,cy+R*.72,cx+R*.75,H*.82,'#4c6682',5);
  line(cx-R*.9,H*.82,cx+R*.9,H*.82,'#8ba9c8',5);
  if(mode==='experiment'){
    const accelTime=Math.max(1,Math.sqrt(2*h/Math.max(.01,9.81*.5)));
    const stopTime=Math.max(2,Math.abs(initialOmega)*I/Math.max(.001,tau));
    if(phase==='ready'){badge.textContent='READY · RELEASE THE MASS';omega=0}
    else if(phase==='falling'){omega=Math.min(initialOmega,initialOmega*(elapsed/accelTime));if(elapsed>accelTime){phase='coast';elapsed=0;initialOmega=Math.max(1,initialOmega)}}
    else if(phase==='coast'){omega=Math.max(0,initialOmega*(1-elapsed/stopTime));if(elapsed>=stopTime){phase='stopped';omega=0}}
    else if(phase==='stopped'){omega=0}
    angle+=omega*dt;
    // Hanging mass and string, visually illustrating unwinding during descent
    const topY=cy-R*.15, bottomY=H*.75;
    const massY=phase==='falling'?topY+(bottomY-topY)*Math.min(1,elapsed/accelTime):(phase==='ready'?topY:bottomY);
    const axleX=cx-R-28, axleY=cy;
    line(axleX,cy-R*.72,axleX,cy+R*.72,'#7d9cbd',8);
    line(axleX,cy-R*.72,axleX,cy+R*.72,'#d7e8fa',2);
    line(axleX,cy,axleX-35,cy,'#ffd166',3);
    line(axleX-35,cy,axleX-35,massY-18,'#ffd166',2);
    ctx.fillStyle='#f0a94b';ctx.fillRect(axleX-49,massY-18,28,36);ctx.strokeStyle='#ffe0a1';ctx.lineWidth=2;ctx.strokeRect(axleX-49,massY-18,28,36);
    ctx.fillStyle='#ffe7b3';ctx.font='bold 13px system-ui';ctx.textAlign='center';ctx.fillText('m',axleX-35,massY+5);
    hint.textContent=phase==='falling'?'Mass descends · wheel accelerates':phase==='coast'?'String detached · wheel slows under friction':phase==='stopped'?'Wheel stopped · reset to repeat':'Click “Release mass” to begin';
  } else {
    angle+=omega*dt;
    hint.textContent='Change rotation speed in the sidebar · watch the yellow reference mark';
  }
  wheel(cx,cy,R,angle);
  // labels and direction cue
  ctx.fillStyle='#d8e9fc';ctx.font='600 14px system-ui';ctx.textAlign='center';ctx.fillText('FLYWHEEL',cx,cy+R+31);
  ctx.fillStyle='#92abc8';ctx.font='12px system-ui';ctx.fillText('AXIS OF ROTATION',cx,cy+R+49);
  ctx.fillStyle='#ffd166';ctx.font='bold 13px system-ui';ctx.textAlign='left';ctx.fillText('↻',cx+R+15,cy-R+12);
  if(mode==='demo'){
    ctx.fillStyle='#eaf2ff';ctx.font='13px system-ui';ctx.textAlign='left';ctx.fillText('AUTO DEMONSTRATION',24,76);ctx.fillStyle='#9fb4cf';ctx.fillText('Rotating reference mark',24,98);
  }
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
window.addEventListener('message',(e)=>{
 if(e.data && e.data.type==='flywheel-release' && mode==='experiment'){phase='falling';elapsed=0;initialOmega=Math.max(3,Math.sqrt(Math.max(.1,2*m*9.81*h/Math.max(I,0.0001))));omega=0;}
 if(e.data && e.data.type==='flywheel-reset' && mode==='experiment'){phase='ready';elapsed=0;omega=0;angle=0;}
});
</script></body></html>
"""
    html = (html.replace("__MODE__", repr(mode))
            .replace("__RPM__", str(float(rpm)))
            .replace("__MASS__", str(float(mass)))
            .replace("__RADIUS__", str(float(radius)))
            .replace("__HEIGHT__", str(float(drop_height)))
            .replace("__INERTIA__", str(float(inertia)))
            .replace("__TAU__", str(float(friction_torque)))
            .replace("__RUNKEY__", str(run_key)))
    components.html(html, height=530, scrolling=False)

st.sidebar.title("⚙️ Control panel")
page = st.sidebar.radio("Navigate", ["Live Simulator", "Theory & Derivation", "Observation Table", "Graphs & Analysis", "Viva Practice"])
mode_label = st.sidebar.radio("Operating mode", ["Automatic demonstration", "Falling-mass experiment"])
mode = "demo" if mode_label == "Automatic demonstration" else "experiment"

if mode == "demo":
    rpm = st.sidebar.slider("Rotation speed (RPM)", 2, 90, 18, help="Changes the automatic demonstration speed.")
    mass, radius, drop_height, inertia, friction_torque = 0.20, 0.020, 0.60, 0.003, 0.001
else:
    rpm = st.sidebar.slider("Reference speed for display (RPM)", 5, 120, 45)
    mass = st.sidebar.slider("Falling mass, m (kg)", 0.05, 1.00, 0.20, 0.01)
    radius = st.sidebar.slider("Axle radius, r (m)", 0.005, 0.050, 0.020, 0.001)
    drop_height = st.sidebar.slider("Drop height, h (m)", 0.10, 1.50, 0.60, 0.05)
    inertia = st.sidebar.number_input("Flywheel moment of inertia I (kg m²)", min_value=0.0001, max_value=1.0, value=0.0030, format="%.5f")
    friction_torque = st.sidebar.number_input("Friction torque τf (N m)", min_value=0.0001, max_value=1.0, value=0.0010, format="%.4f")

st.markdown('<div class="hero"><h1>⚙️ Flywheel Lab Simulator</h1><p class="muted">An interactive rotational dynamics workstation · Built for undergraduate Physics teaching</p></div>', unsafe_allow_html=True)

if page == "Live Simulator":
    left, right = st.columns([1.8, 1])
    with left:
        st.subheader("Live apparatus")
        if mode == "experiment":
            st.caption("Use the controls below to release the mass. The canvas animation runs in the browser independently of Streamlit reruns.")
        else:
            st.caption("The flywheel begins rotating automatically. Adjust RPM in the sidebar and observe the yellow reference mark.")
        flywheel_animation(mode, rpm, mass, radius, drop_height, inertia, friction_torque, int(time.time()))
        if mode == "experiment":
            c1, c2 = st.columns(2)
            if c1.button("▶ Release mass", type="primary", use_container_width=True):
                components.html("<script>parent.postMessage({type:'flywheel-release'}, '*');</script>", height=0)
                st.session_state["released"] = True
            if c2.button("↻ Reset experiment", use_container_width=True):
                components.html("<script>parent.postMessage({type:'flywheel-reset'}, '*');</script>", height=0)
                st.session_state["released"] = False
            st.info("Browser components are isolated. If your browser does not pass the release command to the canvas, use the live animation as a visual model and use the calculations below for the numerical experiment.")
    with right:
        st.subheader("Live physics panel")
        omega_demo = 2 * math.pi * rpm / 60
        st.metric("Selected angular speed", f"{omega_demo:.2f} rad/s")
        st.metric("Selected rotation rate", f"{rpm} RPM")
        st.metric("Falling mass", f"{mass:.3f} kg")
        st.metric("Axle radius", f"{radius:.3f} m")
        st.markdown("#### What to notice")
        st.write("1. The yellow marker makes angular displacement visible.")
        st.write("2. A larger RPM means a greater angular speed.")
        st.write("3. In the real experiment, friction gradually reduces the wheel's speed after the string detaches.")
        st.caption("The automatic demo is illustrative; it is not a measurement of a real apparatus.")

elif page == "Theory & Derivation":
    st.header("Physics behind the flywheel")
    st.subheader("1. Torque and rotational dynamics")
    st.latex(r"\\tau_{\\mathrm{net}}=I\\alpha")
    st.write("During the fall, the string tension produces a driving torque while bearing friction opposes rotation.")
    st.latex(r"Tr-\\tau_f=I\\alpha")
    st.subheader("2. Falling mass and energy balance")
    st.latex(r"mgh=\\frac12 mv^2+\\frac12 I\\omega^2+n_1W_f")
    st.write("The lost gravitational potential energy becomes translational kinetic energy, rotational kinetic energy, and energy dissipated by friction.")
    st.subheader("3. Angular speed after detachment")
    st.write("If angular deceleration is approximately constant and the wheel makes n₂ further revolutions in stopping time t:")
    st.latex(r"\\theta=2\\pi n_2=\\frac{\\omega+0}{2}t")
    st.latex(r"\\boxed{\\omega=\\frac{4\\pi n_2}{t}}")
    st.subheader("4. Moment of inertia")
    st.latex(r"h=2\\pi r n_1,\\qquad v=r\\omega")
    st.latex(r"\\boxed{I=\\frac{m\\left(\\frac{2gh}{\\omega^2}-r^2\\right)}{1+n_1/n_2}}")
    st.warning("Assumptions: approximately constant angular deceleration after detachment and approximately constant frictional work per revolution. Use measured values from your apparatus for a laboratory result.")

elif page == "Observation Table":
    st.header("Observation workstation")
    st.write("Enter actual measurements below, or use the default example rows to demonstrate the calculation. These sample rows are illustrative only.")
    if "trials" not in st.session_state:
        st.session_state.trials = pd.DataFrame([
            {"Trial": 1, "Mass m (kg)": 0.20, "Axle radius r (m)": 0.020, "Turns n1": 5, "Extra turns n2": 20, "Stopping time t (s)": 10.0},
            {"Trial": 2, "Mass m (kg)": 0.20, "Axle radius r (m)": 0.020, "Turns n1": 5, "Extra turns n2": 21, "Stopping time t (s)": 10.4},
            {"Trial": 3, "Mass m (kg)": 0.20, "Axle radius r (m)": 0.020, "Turns n1": 5, "Extra turns n2": 19, "Stopping time t (s)": 9.7},
        ])
    edited = st.data_editor(st.session_state.trials, num_rows="dynamic", use_container_width=True, key="trial_editor")
    st.session_state.trials = edited
    results = []
    for _, row in edited.iterrows():
        try:
            m0, r0 = float(row["Mass m (kg)"]), float(row["Axle radius r (m)"])
            n1, n2, t0 = float(row["Turns n1"]), float(row["Extra turns n2"]), float(row["Stopping time t (s)"])
            if min(m0, r0, n1, n2, t0) <= 0:
                I0 = np.nan
            else:
                h0 = 2 * math.pi * r0 * n1
                w0 = 4 * math.pi * n2 / t0
                I0 = m0 * (2 * G * h0 / w0**2 - r0**2) / (1 + n1/n2)
                if I0 <= 0:
                    I0 = np.nan
            results.append({"Trial": row["Trial"], "Calculated I (kg m²)": I0})
        except (ValueError, TypeError, ZeroDivisionError, KeyError):
            results.append({"Trial": row.get("Trial", "?"), "Calculated I (kg m²)": np.nan})
    result_df = pd.DataFrame(results)
    merged = pd.concat([edited.reset_index(drop=True), result_df[["Calculated I (kg m²)"]]], axis=1)
    st.dataframe(merged, use_container_width=True)
    valid = result_df["Calculated I (kg m²)"].dropna()
    if len(valid):
        st.metric("Mean moment of inertia", f"{valid.mean():.5g} kg m²")
        if len(valid) > 1:
            st.metric("Sample standard deviation", f"{valid.std(ddof=1):.3g} kg m²")
    else:
        st.error("No valid trials. Check that all entered quantities are positive and the calculated inertia is physically meaningful.")
    st.download_button("Download observations as CSV", merged.to_csv(index=False).encode("utf-8"), "flywheel_observations.csv", "text/csv")

elif page == "Graphs & Analysis":
    st.header("Graphs & analysis")
    st.subheader("Angular velocity during free rotation")
    omega0 = 2 * math.pi * rpm / 60
    t_stop = st.slider("Illustrative stopping time (s)", 2.0, 30.0, 10.0, 0.5)
    ts = np.linspace(0, t_stop, 150)
    ws = omega0 * (1 - ts/t_stop)
    ws[ws < 0] = 0
    fig = px.line(x=ts, y=ws, labels={"x":"Time after detachment (s)", "y":"Angular velocity (rad/s)"}, title="Idealized constant-angular-deceleration model")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.latex(r"\\omega(t)=\\omega_0\\left(1-\\frac{t}{t_{\\mathrm{stop}}}\\right),\\quad 0\\leq t\\leq t_{\\mathrm{stop}}")
    st.caption("Illustrative model: actual friction may vary with speed, bearing condition, and alignment.")

else:
    st.header("Viva practice")
    questions = [
        ("What is the SI unit of moment of inertia?", ["kg m²", "N m", "kg/m²", "J/s"], 0, "Moment of inertia has dimensions mass × length squared."),
        ("Why does the flywheel continue rotating after the string detaches?", ["Gravity continues pulling it", "It has angular momentum and rotational kinetic energy", "The axle keeps driving it", "Its moment of inertia becomes zero"], 1, "The wheel continues rotating, while friction gradually removes its rotational energy."),
        ("What does bearing friction do after detachment?", ["Increases angular speed", "Reduces angular speed", "Changes the wheel's mass", "Makes the axle radius larger"], 1, "Friction produces an opposing torque and causes angular deceleration."),
        ("For constant angular deceleration from ω₀ to rest, the average angular speed is:", ["ω₀", "2ω₀", "ω₀/2", "Zero at all times"], 2, "For uniform deceleration from ω₀ to zero, the average is (ω₀ + 0)/2."),
    ]
    for i, (q, options, answer, explanation) in enumerate(questions):
        choice = st.radio(f"{i+1}. {q}", options, key=f"q_{i}")
        if st.button("Check answer", key=f"check_{i}"):
            if options.index(choice) == answer:
                st.success("Correct. " + explanation)
            else:
                st.error("Not quite. " + explanation)
    st.caption("Use these questions for a quick classroom viva; ask students to explain their reasoning aloud.")
