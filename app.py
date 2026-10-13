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

def flywheel_animation(mode, rpm, mass, radius, drop_height, inertia, friction_torque, run_key, released=False):
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
const mode=__MODE__, targetRPM=__RPM__, m=__MASS__, r=__RADIUS__, h=__HEIGHT__, I=__INERTIA__, tau=__TAU__, runKey=__RUNKEY__, released=__RELEASED__;
let angle=0, last=0, elapsed=0, phase=mode==='experiment'?(released?'falling':'ready'):'demo', omega=targetRPM*2*Math.PI/60, initialOmega=Math.max(3,Math.sqrt(Math.max(.1,2*m*9.81*h/Math.max(I,0.0001))));
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
            .replace("__RUNKEY__", str(run_key))
            .replace("__RELEASED__", "true" if released else "false"))
    components.html(html, height=530, scrolling=False)

st.sidebar.title("⚙️ Control panel")
page = st.sidebar.radio("Navigate", ["Live Simulator", "Why a Flywheel?", "Visual Playground", "Theory & Derivation", "Observation Table", "Graphs & Analysis", "Advanced Dynamics", "Design Studio", "Uncertainty & Report", "Viva Practice"])
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
        flywheel_animation(mode, rpm, mass, radius, drop_height, inertia, friction_torque, int(time.time()), st.session_state.get('released', False))
        if mode == "experiment":
            c1, c2 = st.columns(2)
            if c1.button("▶ Release mass", type="primary", use_container_width=True):
                st.session_state["released"] = True
                st.rerun()
            if c2.button("↻ Reset experiment", use_container_width=True):
                st.session_state["released"] = False
                st.rerun()
            st.caption("Release restarts the browser animation in the falling stage; reset returns it to the initial condition.")
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


elif page == "Why a Flywheel?":
    st.markdown("""
    <div style="padding:28px;border-radius:22px;background:linear-gradient(120deg,#123456,#17223b);border:1px solid #52718f">
    <div style="letter-spacing:3px;color:#9bdcff">THE BIG IDEA</div>
    <h1>Why do machines need a flywheel?</h1>
    <p style="font-size:19px;color:#d1e2f5">A flywheel stores rotational energy when the driving system supplies extra energy and releases some when the drive weakens. The result is smoother rotation.</p></div>
    """, unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    with left:
        fluct = st.slider("Drive fluctuation", 0.0, 0.9, 0.65, 0.05)
        inertia_visual = st.slider("Flywheel size / inertia", 0.2, 5.0, 2.5, 0.1)
        base_speed = st.slider("Average speed (relative units)", 30, 180, 90, 5)
        st.markdown("#### Think of it like this")
        st.write("**Surplus drive:** the wheel stores energy.")
        st.write("**Weak drive:** the wheel releases energy.")
        st.write("**Net effect:** less variation in speed across a cycle.")
    with right:
        tv = np.linspace(0, 8, 500)
        raw = base_speed * (1 + fluct*np.sin(2*np.pi*tv))
        attenuated = fluct/(1+1.8*inertia_visual)
        smooth = base_speed * (1 + attenuated*np.sin(2*np.pi*tv))
        df = pd.DataFrame({"Time (s)":np.r_[tv,tv],"Relative speed":np.r_[raw,smooth],"System":["Without flywheel"]*len(tv)+["With flywheel"]*len(tv)})
        fig = px.line(df,x="Time (s)",y="Relative speed",color="System",title="Speed fluctuation: conceptual comparison")
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)
    st.info("This graph is an illustrative teaching model, not measured data from a particular machine. A flywheel reduces cyclic speed variation; it does not create energy or guarantee perfectly constant speed.")
    st.subheader("Where flywheels are useful")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("### Engine")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Flywheel.jpg/640px-Flywheel.jpg",use_container_width=True)
        st.caption("Helps smooth torque pulses between power strokes.")
    with c2:
        st.markdown("### Industrial machine")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Flywheel.jpg/640px-Flywheel.jpg",use_container_width=True)
        st.caption("Helps handle short-term changes in load.")
    with c3:
        st.markdown("### Energy storage")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Flywheel_energy_storage.jpg/640px-Flywheel_energy_storage.jpg",use_container_width=True)
        st.caption("A rotating mass can store energy for later release.")
    st.caption("External images require an internet connection; the graph is generated locally.")

elif page == "Visual Playground":
    st.header("Visual Playground")
    st.caption("A more visual, classroom-friendly rotor explorer.")
    style = st.selectbox("Flywheel design",["Classic spokes","Solid disk","Heavy rim","Precision rotor"])
    rpm_vis = st.slider("Rotation speed (RPM)",1,180,35,key="visual_rpm")
    spoke_count = st.slider("Number of spokes",4,16,8,2)
    trails = st.toggle("Motion trail",True)
    labels = st.toggle("Component labels",True)
    style_key = {"Classic spokes":"spokes","Solid disk":"disk","Heavy rim":"rim","Precision rotor":"precision"}[style]
    html = r"""
    <div style="background:radial-gradient(ellipse at center,#1b3553,#07101c);border:1px solid #385270;border-radius:20px;overflow:hidden"><canvas id="rotor" style="width:100%;height:520px;display:block"></canvas></div>
    <script>
    const cv=document.getElementById('rotor'),ctx=cv.getContext('2d'),kind='__STYLE__',rpm=__RPM__,n=__N__,trailOn=__TRAIL__,labels=__LABEL__;
    let a=0,last=0,tail=[];
    function size(){const d=window.devicePixelRatio||1;cv.width=cv.clientWidth*d;cv.height=520*d;ctx.setTransform(d,0,0,d,0,0)}size();window.addEventListener('resize',size);
    function draw(t){let dt=last?Math.min(.04,(t-last)/1000):0;last=t;a+=rpm*2*Math.PI/60*dt;
      const W=cv.clientWidth,H=520,cx=W/2,cy=H/2-10,R=Math.min(W*.30,190);ctx.clearRect(0,0,W,H);
      let g=ctx.createRadialGradient(cx-R*.2,cy-R*.2,5,cx,cy,R);g.addColorStop(0,'#42688d');g.addColorStop(1,'#102035');
      ctx.beginPath();ctx.arc(cx,cy,R,0,2*Math.PI);ctx.fillStyle=kind==='disk'?'#243c56':g;ctx.fill();
      ctx.save();ctx.translate(cx,cy);ctx.rotate(a);
      ctx.beginPath();ctx.arc(0,0,R-4,0,2*Math.PI);ctx.lineWidth=kind==='rim'?28:8;ctx.strokeStyle='#a9c4e2';ctx.stroke();
      if(kind!=='disk'){for(let i=0;i<n;i++){let q=2*Math.PI*i/n;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo((R-14)*Math.cos(q),(R-14)*Math.sin(q));ctx.strokeStyle=i%2?'#72d8ff':'#e4f0ff';ctx.lineWidth=kind==='precision'?3:6;ctx.stroke()}}
      if(kind==='precision'){ctx.beginPath();ctx.arc(0,0,R*.58,0,2*Math.PI);ctx.strokeStyle='#ffd166';ctx.lineWidth=3;ctx.stroke()}
      ctx.beginPath();ctx.arc(0,0,13,0,2*Math.PI);ctx.fillStyle='#f4f8ff';ctx.fill();
      ctx.beginPath();ctx.arc(R-7,0,7,0,2*Math.PI);ctx.fillStyle='#ffd166';ctx.fill();ctx.restore();
      tail.push([cx+(R-7)*Math.cos(a),cy+(R-7)*Math.sin(a)]);if(tail.length>42)tail.shift();
      if(trailOn){ctx.beginPath();tail.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.strokeStyle='rgba(255,209,102,.55)';ctx.lineWidth=2;ctx.stroke()}
      ctx.textAlign='center';ctx.fillStyle='#eaf2ff';ctx.font='600 15px system-ui';ctx.fillText('LIVE FLYWHEEL',cx,cy+R+32);ctx.fillStyle='#a8bfd9';ctx.font='13px system-ui';ctx.fillText(rpm+' RPM  ·  '+(rpm*2*Math.PI/60).toFixed(2)+' rad/s',cx,cy+R+54);
      if(labels){ctx.textAlign='left';ctx.fillStyle='#c4d9ef';ctx.fillText('AXLE',cx+16,cy-10);ctx.fillText('RIM',cx+R*.55,cy-R*.55)}
      requestAnimationFrame(draw)}requestAnimationFrame(draw);
    </script>
    """
    html=html.replace("__STYLE__",style_key).replace("__RPM__",str(rpm_vis)).replace("__N__",str(spoke_count)).replace("__TRAIL__","true" if trails else "false").replace("__LABEL__","true" if labels else "false")
    components.html(html,height=545,scrolling=False)
    st.markdown("### Try this in class")
    st.write("Switch between a solid disk and a heavy rim. Ask students what they notice about the material distribution and why it can affect rotational inertia.")

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


elif page == "Advanced Dynamics":
    st.header("Advanced rotational dynamics")
    st.caption("Explore the flywheel as a dynamical system, not just as a rotating picture.")
    tab1, tab2, tab3 = st.tabs(["Torque model", "Energy ledger", "Motion explorer"])
    with tab1:
        st.subheader("Coupled falling mass and flywheel")
        st.latex(r"mg-T=ma,\qquad Tr-\tau_f=I\alpha,\qquad a=r\alpha")
        m_adv = st.slider("Falling mass (kg)", 0.05, 1.00, 0.20, 0.01, key="adv_m")
        r_adv = st.slider("Axle radius (m)", 0.005, 0.050, 0.020, 0.001, key="adv_r")
        I_adv = st.slider("Flywheel inertia (kg m²)", 0.0005, 0.0500, 0.0030, 0.0005, format="%.4f", key="adv_I")
        tau_adv = st.slider("Opposing friction torque (N m)", 0.0, 0.050, 0.001, 0.0005, format="%.4f", key="adv_tau")
        effective = I_adv + m_adv * r_adv**2
        alpha_adv = (m_adv * G * r_adv - tau_adv) / (I_adv + m_adv * r_adv**2)
        if alpha_adv > 0:
            a_adv = r_adv * alpha_adv
            tension = m_adv * (G - a_adv)
            st.success("The mass accelerates downward for these parameters.")
        else:
            a_adv, tension = 0.0, float("nan")
            st.warning("The selected friction torque is at least as large as the driving torque; spontaneous downward acceleration is not predicted by this idealized model.")
        x1, x2, x3 = st.columns(3)
        x1.metric("Angular acceleration", f"{alpha_adv:.3f} rad/s²")
        x2.metric("Linear acceleration", f"{a_adv:.3f} m/s²")
        x3.metric("String tension", f"{tension:.3f} N" if np.isfinite(tension) else "No descent")
        st.markdown("**Model assumptions:** no slip between string and axle, negligible string mass, constant axle radius, and constant opposing friction torque.")
    with tab2:
        st.subheader("Energy ledger for a falling mass")
        m_e = st.number_input("Mass (kg)", 0.01, 5.0, 0.20, 0.01, key="energy_m")
        h_e = st.number_input("Drop height (m)", 0.01, 5.0, 0.60, 0.01, key="energy_h")
        v_e = st.number_input("Mass speed at detachment (m/s)", 0.0, 20.0, 0.80, 0.05, key="energy_v")
        w_e = st.number_input("Flywheel angular speed (rad/s)", 0.0, 500.0, 25.0, 0.5, key="energy_w")
        I_e = st.number_input("Flywheel inertia (kg m²)", 0.0001, 10.0, 0.003, 0.0001, format="%.4f", key="energy_I")
        Ein = m_e * G * h_e
        transl = 0.5 * m_e * v_e**2
        rot = 0.5 * I_e * w_e**2
        residual = Ein - transl - rot
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Potential energy lost", f"{Ein:.4f} J")
        c2.metric("Translational KE", f"{transl:.4f} J")
        c3.metric("Rotational KE", f"{rot:.4f} J")
        c4.metric("Unaccounted energy", f"{residual:.4f} J")
        if residual < -1e-9:
            st.error("The kinetic-energy total exceeds the available gravitational potential energy. Check the inputs or model assumptions.")
        else:
            st.info("The residual represents energy available for frictional dissipation and other losses under this simplified ledger.")
        ledger = pd.DataFrame({"Energy term":["Potential energy lost","Translational kinetic energy","Rotational kinetic energy","Residual / losses"],"Energy (J)":[Ein,transl,rot,max(0,residual)]})
        fig_energy = px.bar(ledger, x="Energy term", y="Energy (J)", title="Energy distribution")
        fig_energy.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_energy, use_container_width=True)
    with tab3:
        st.subheader("Angular motion under constant friction torque")
        I_m = st.number_input("Moment of inertia (kg m²)", min_value=0.0001, value=0.0030, format="%.5f", key="motion_I")
        rpm_m = st.slider("Initial angular speed (RPM)", 5, 300, 90, key="motion_rpm")
        tau_m = st.slider("Friction torque (N m)", 0.0001, 0.0200, 0.0010, 0.0001, format="%.4f", key="motion_tau")
        w0 = rpm_m * 2 * math.pi / 60
        decel = tau_m / I_m
        t_stop_m = w0 / decel
        tt = np.linspace(0, t_stop_m, 250)
        ww = np.maximum(0, w0 - decel * tt)
        theta = w0 * tt - 0.5 * decel * tt**2
        frame = pd.DataFrame({"Time (s)":tt,"Angular velocity (rad/s)":ww,"Angular displacement (rad)":theta})
        fig_m = px.line(frame, x="Time (s)", y="Angular velocity (rad/s)", title="Predicted spin-down")
        fig_m.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_m, use_container_width=True)
        st.metric("Predicted stopping time", f"{t_stop_m:.2f} s")
        st.metric("Predicted turns before rest", f"{theta[-1]/(2*math.pi):.2f} revolutions")
        st.caption("This idealized model assumes a constant friction torque. Real bearings may exhibit speed-dependent and static friction.")

elif page == "Design Studio":
    st.header("Flywheel design studio")
    st.caption("Compare idealized mass distributions and see how geometry affects rotational inertia.")
    geometry = st.selectbox("Idealized geometry", ["Uniform solid disk", "Thin ring", "Thick-walled cylinder"])
    M = st.slider("Flywheel mass (kg)", 0.1, 20.0, 2.0, 0.1)
    R = st.slider("Outer radius (m)", 0.05, 1.0, 0.30, 0.01)
    if geometry == "Uniform solid disk":
        I_geom = 0.5 * M * R**2
        formula = r"I=\frac{1}{2}MR^2"
    elif geometry == "Thin ring":
        I_geom = M * R**2
        formula = r"I=MR^2"
    else:
        ri = st.slider("Inner radius (m)", 0.0, max(0.01, R-0.01), min(0.15, R-0.01), 0.01)
        I_geom = 0.5 * M * (R**2 + ri**2)
        formula = r"I=\frac{1}{2}M(R_o^2+R_i^2)"
    rpm_d = st.slider("Operating speed (RPM)", 10, 1000, 120, 10)
    w_d = rpm_d * 2 * math.pi / 60
    st.latex(formula)
    a, b, c = st.columns(3)
    a.metric("Moment of inertia", f"{I_geom:.5f} kg m²")
    b.metric("Rotational kinetic energy", f"{0.5*I_geom*w_d**2:.3f} J")
    c.metric("Angular momentum", f"{I_geom*w_d:.3f} kg m²/s")
    comparison = pd.DataFrame({"Model":["Solid disk","Thin ring"],"Moment of inertia (kg m²)":[0.5*M*R**2,M*R**2]})
    fig_d = px.bar(comparison, x="Model", y="Moment of inertia (kg m²)", title="Effect of mass distribution")
    fig_d.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_d, use_container_width=True)
    st.info("For the same mass and outer radius, more mass concentrated near the rim gives a larger moment of inertia.")

elif page == "Uncertainty & Report":
    st.header("Uncertainty analysis & lab report")
    st.write("Estimate how timing and rotation-count uncertainty propagate into the calculated moment of inertia. Enter measured values and their approximate uncertainties.")
    m_u = st.number_input("Falling mass m (kg)", 0.001, 5.0, 0.200, 0.001, key="u_m")
    dm_u = st.number_input("Mass uncertainty Δm (kg)", 0.0, 0.5, 0.001, 0.001, key="u_dm")
    r_u = st.number_input("Axle radius r (m)", 0.0001, 0.2, 0.020, 0.0001, format="%.4f", key="u_r")
    dr_u = st.number_input("Radius uncertainty Δr (m)", 0.0, 0.05, 0.0005, 0.0001, format="%.4f", key="u_dr")
    n1_u = st.number_input("Turns during fall n₁", 0.1, 1000.0, 5.0, 0.5, key="u_n1")
    n2_u = st.number_input("Extra turns n₂", 0.1, 1000.0, 20.0, 0.5, key="u_n2")
    t_u = st.number_input("Stopping time t (s)", 0.01, 10000.0, 10.0, 0.1, key="u_t")
    dt_u = st.number_input("Timing uncertainty Δt (s)", 0.0, 100.0, 0.2, 0.05, key="u_dt")
    h_u = 2 * math.pi * r_u * n1_u
    w_u = 4 * math.pi * n2_u / t_u
    I_u = m_u * (2*G*h_u/w_u**2-r_u**2)/(1+n1_u/n2_u)
    if I_u <= 0:
        st.error("These values yield a non-positive inertia estimate. Review measurements and assumptions before reporting.")
    else:
        # Monte Carlo propagation; illustrative uncertainties for n1/n2 are treated as exact counts here.
        rng = np.random.default_rng(2026)
        samples = 30000
        ms = np.maximum(1e-9, rng.normal(m_u, max(dm_u, 1e-12), samples))
        rs = np.maximum(1e-9, rng.normal(r_u, max(dr_u, 1e-12), samples))
        tsamp = np.maximum(1e-6, rng.normal(t_u, max(dt_u, 1e-12), samples))
        hs = 2 * math.pi * rs * n1_u
        wsamp = 4 * math.pi * n2_u / tsamp
        Is = ms * (2*G*hs/wsamp**2-rs**2)/(1+n1_u/n2_u)
        Is = Is[np.isfinite(Is) & (Is > 0)]
        if len(Is) > 100:
            low, high = np.percentile(Is, [2.5, 97.5])
            st.metric("Moment of inertia estimate", f"{I_u:.6g} kg m²")
            st.metric("Monte Carlo 95% interval", f"[{low:.6g}, {high:.6g}] kg m²")
            st.caption(f"Monte Carlo used {samples:,} samples. This interval only reflects the entered mass, radius, and timing uncertainties; it does not include systematic errors or uncertainty in the rotation counts.")
        report = f"""FLYWHEEL EXPERIMENT — LAB REPORT DRAFT

Aim:
To estimate the moment of inertia of a flywheel using the falling-mass method.

Measured / entered values:
Mass m = {m_u:.6g} kg
Axle radius r = {r_u:.6g} m
Turns during descent n1 = {n1_u:g}
Additional turns n2 = {n2_u:g}
Stopping time t = {t_u:.6g} s
Drop height h = {h_u:.6g} m
Angular speed at detachment ω = {w_u:.6g} rad/s

Calculation:
I = m(2gh/ω² - r²)/(1 + n1/n2)
I = {I_u:.8g} kg m²

Assumptions and limitations:
Approximately constant angular deceleration after detachment; approximately constant frictional work per revolution; uncertainty interval does not include systematic errors.

Result:
The estimated moment of inertia is {I_u:.8g} kg m², subject to the stated assumptions and measurement uncertainties.
"""
        st.text_area("Report preview", report, height=340)
        st.download_button("Download report draft (.txt)", report, file_name="flywheel_lab_report.txt", mime="text/plain")

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
