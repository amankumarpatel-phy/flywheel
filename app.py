import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Flywheel 3D Lab", page_icon="⚙️", layout="wide")
st.markdown("""
<style>
.stApp{background:#070b14;color:#e9f1ff}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.1rem;max-width:1600px}
h1,h2,h3{color:#eff6ff}
div[data-testid="stMarkdownContainer"] p{color:#aabbd1}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="padding:22px 26px;border:1px solid #263952;border-radius:20px;background:linear-gradient(115deg,#12243b,#0b1220);margin-bottom:12px">
<div style="font-size:11px;letter-spacing:4px;color:#6dd6ff;font-weight:800">VIRTUAL MECHANICS LAB · 01</div>
<h1 style="margin:8px 0 2px;font-size:38px">FLYWHEEL / 3D APPARATUS</h1>
<p style="margin:0;color:#9fb4ce">Explore the machine from every angle. Run a falling-mass experiment or spin the rotor freely.</p>
</div>
""", unsafe_allow_html=True)

html = r"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#070b14;color:#e8f1ff;font-family:Inter,system-ui,Arial}
.lab{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:12px;min-height:690px}
.stage{position:relative;border:1px solid #26374e;border-radius:16px;overflow:hidden;background:radial-gradient(ellipse at 50% 40%,#15263c,#080d17 72%)}
#view{height:570px;width:100%;display:block;cursor:grab}#view:active{cursor:grabbing}
.overlay{position:absolute;left:14px;top:14px;display:flex;gap:7px;flex-wrap:wrap;pointer-events:none}
.pill{background:#101d2ee8;border:1px solid #344b66;border-radius:8px;padding:7px 10px;font-size:10px;letter-spacing:1.5px;color:#b7d8f5}
.help{position:absolute;bottom:12px;left:14px;color:#8fa5c0;font-size:11px;background:#08111ddd;padding:8px 10px;border-radius:8px}
.controls{border:1px solid #26374e;border-radius:16px;background:#0b1320;padding:16px;display:flex;flex-direction:column;gap:13px}
.eyebrow{font-size:10px;letter-spacing:2px;color:#6dd6ff;font-weight:800}.title{font-size:17px;font-weight:750;margin-top:4px}
label{font-size:11px;color:#a6bad2;display:flex;justify-content:space-between;margin-bottom:7px}
label b{color:#edf6ff;font-weight:650}input[type=range]{width:100%;accent-color:#61d5ff}
select{width:100%;background:#101e30;border:1px solid #30445e;color:#eaf3ff;border-radius:8px;padding:10px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:7px}
button{border:1px solid #31465f;border-radius:9px;padding:10px 8px;color:#dbeaff;background:#132238;font-weight:700;cursor:pointer}
button.primary{background:#69d8ff;color:#06101a;border-color:#69d8ff}button:hover{filter:brightness(1.12)}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px}
.metric{border:1px solid #26374e;background:#0b1320;border-radius:12px;padding:13px}
.metric small{display:block;color:#8fa6c1;font-size:10px;letter-spacing:1px;text-transform:uppercase}
.metric strong{display:block;font-size:22px;margin-top:7px;color:#f2f8ff;font-variant-numeric:tabular-nums}
.metric em{font-size:10px;color:#7c94b2;font-style:normal}
.readout{font-size:12px;line-height:1.65;color:#a9bdd4;border-top:1px solid #26374e;padding-top:12px}
.note{border:1px solid #26374e;background:#0b1320;border-radius:12px;padding:15px;margin-top:10px;color:#9fb4ce;font-size:12px;line-height:1.65}
@media(max-width:850px){.lab{grid-template-columns:1fr}.controls{display:grid;grid-template-columns:1fr 1fr}.controls .full{grid-column:1/-1}#view{height:440px}.metrics{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<div style="padding:10px">
<div class="lab">
<section>
<div class="stage"><canvas id="view"></canvas>
<div class="overlay"><span class="pill">● 3D SCENE</span><span class="pill" id="status">AUTO ROTATION</span><span class="pill">ORBIT · ZOOM · PAN</span></div>
<div class="help">Drag to orbit · scroll to zoom · right-drag to pan</div></div>
<div class="metrics">
<div class="metric"><small>Angular speed</small><strong id="rpmout">42.0</strong><em>RPM</em></div>
<div class="metric"><small>Angular velocity</small><strong id="wout">4.40</strong><em>rad s⁻¹</em></div>
<div class="metric"><small>Angular accel.</small><strong id="aout">0.00</strong><em>rad s⁻²</em></div>
<div class="metric"><small>Elapsed time</small><strong id="tout">0.00</strong><em>seconds</em></div>
</div>
<div class="note"><b style="color:#e8f3ff">LAB NOTE</b><br><span id="explain">The rotor is spinning freely. The yellow marker makes angular displacement visible.</span><br><span style="color:#718aa8">Visual dimensions are illustrative; numerical readouts use the idealized model and selected parameters.</span></div>
</section>
<aside class="controls">
<div class="full"><div class="eyebrow">INSTRUMENT PANEL</div><div class="title">Run the experiment</div></div>
<div class="full"><label>Experiment mode</label><select id="mode"><option value="free">Free rotation</option><option value="fall">Falling-mass experiment</option></select></div>
<div class="full"><label>Rotor design <b id="designlabel">Spoked wheel</b></label><select id="design"><option value="spoke">Spoked wheel</option><option value="disk">Solid disk</option><option value="rim">Heavy rim</option><option value="precision">Precision rotor</option></select></div>
<div class="full"><label>Display speed <b id="rpmval">42 RPM</b></label><input id="rpm" type="range" min="5" max="180" value="42"></div>
<div class="full"><label>Falling mass <b id="massval">200 g</b></label><input id="mass" type="range" min="50" max="800" value="200" step="10"></div>
<div class="full"><label>Axle radius <b id="radiusval">20 mm</b></label><input id="radius" type="range" min="8" max="40" value="20" step="1"></div>
<div class="full"><label>Rotor inertia <b id="ival">0.0030 kg m²</b></label><input id="inertia" type="range" min="5" max="100" value="30"></div>
<div class="full"><label>Friction torque <b id="tauval">0.0010 N m</b></label><input id="tau" type="range" min="0" max="50" value="10"></div>
<div class="full"><label>Animation time <b id="speedval">1.0×</b></label><input id="speed" type="range" min="25" max="200" value="100" step="25"></div>
<div class="row full"><button class="primary" id="start">▶ Start</button><button id="reset">↺ Reset</button></div>
<div class="row full"><button id="cam">◎ Front view</button><button id="stop">Ⅱ Pause</button></div>
<div class="readout full"><div class="eyebrow">LIVE MODEL</div><div id="equations">ω = 2π × RPM / 60<br>α = 0 during ideal free rotation</div><div style="margin-top:8px">Drag with the mouse to inspect the axle, rim, supports and hanging mass from different angles.</div></div>
</aside></div></div>
<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import {OrbitControls} from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
const canvas=document.getElementById('view');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(canvas.clientWidth,canvas.clientHeight,false);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene();scene.background=new THREE.Color('#0b1422');scene.fog=new THREE.Fog('#0b1422',12,28);
const camera=new THREE.PerspectiveCamera(42,canvas.clientWidth/canvas.clientHeight,.1,100);camera.position.set(5.4,3.5,7.3);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.target.set(0,1.85,0);orbit.enableDamping=true;orbit.dampingFactor=.07;orbit.minDistance=3.5;orbit.maxDistance=13;
scene.add(new THREE.HemisphereLight(0xb9dcff,0x182131,2.1));
const key=new THREE.DirectionalLight(0xffffff,3.2);key.position.set(4,8,5);key.castShadow=true;scene.add(key);
const rimLight=new THREE.PointLight(0x49bfff,18,10);rimLight.position.set(-3,3,2);scene.add(rimLight);
const mat=(color,metalness=.2,roughness=.35)=>new THREE.MeshStandardMaterial({color,metalness,roughness});
const steel=mat('#829bb5',.8,.25), darkSteel=mat('#27384d',.75,.3), bright=mat('#d4e7fa',.8,.2), gold=mat('#ffd166',.65,.25), blue=mat('#3ca8d8',.6,.28), black=mat('#121d2a',.25,.4), massMat=mat('#e6a34c',.45,.3);
function box(parent,x,y,z,sx,sy,sz,material){const o=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),material);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
function cyl(parent,r1,r2,len,x,y,z,material,axis='y',segments=48){const o=new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,len,segments),material);o.position.set(x,y,z);if(axis==='x')o.rotation.z=Math.PI/2;if(axis==='z')o.rotation.x=Math.PI/2;o.castShadow=true;o.receiveShadow=true;parent.add(o);return o}
const floor=new THREE.Mesh(new THREE.PlaneGeometry(200,200),mat('#0b1320',.15,.8));floor.rotation.x=-Math.PI/2;floor.position.y=-.03;floor.receiveShadow=true;scene.add(floor);
const grid=new THREE.GridHelper(18,36,'#29405a','#17273a');grid.position.y=-.015;scene.add(grid);
// Base plate and rubber feet
box(scene,0,.12,0,4.8,.22,2.3,darkSteel);
for(const x of [-1.8,1.8])for(const z of [-.75,.75])cyl(scene,.16,.16,.16,x,.0,z,black,'y',32);
// Main uprights and cross braces
for(const x of [-1.25,1.25]){box(scene,x,1.15,0,.16,1.95,.22,steel);box(scene,x*.78,.9,0,.1,1.1,.12,darkSteel)}
box(scene,0,2.1,0,2.8,.16,.3,steel);
const CY=2.15, R=1.25, AXZ=0;
const rotor=new THREE.Group();rotor.position.set(0,CY,AXZ);scene.add(rotor);
// wheel lies in XY plane and spins around Z axle
const outer=cyl(rotor,R,R,.16,0,0,0,steel,'z',96);
const innerRing=cyl(rotor,R*.88,R*.88,.18,0,0,0,darkSteel,'z',96);
const torus=new THREE.Mesh(new THREE.TorusGeometry(R*.91,.075,14,100),bright);rotor.add(torus);
const innerTorus=new THREE.Mesh(new THREE.TorusGeometry(R*.65,.025,8,80),blue);rotor.add(innerTorus);
const spokes=new THREE.Group();rotor.add(spokes);
for(let i=0;i<8;i++){const a=i*Math.PI/4;const s=box(spokes,Math.cos(a)*R*.43,Math.sin(a)*R*.43,0,R*.82,.075,.12,i%2?steel:bright);s.rotation.z=a}
cyl(rotor,.34,.34,.24,0,0,0,bright,'z',64);
cyl(rotor,.22,.22,.3,0,0,.02,gold,'z',48);
cyl(rotor,.11,.11,.38,0,0,.03,darkSteel,'z',48);
const marker=new THREE.Mesh(new THREE.SphereGeometry(.085,20,16),gold);marker.position.set(0,R*.91,.12);rotor.add(marker);
// axle, bearing blocks, collars and mount
cyl(scene,.11,.11,3.7,0,CY,0,bright,'z',48);
for(const x of [-1.48,1.48]){box(scene,x,CY,0,.36,.52,.55,darkSteel);cyl(scene,.2,.2,.6,x,CY,0,steel,'z',48);cyl(scene,.12,.12,.63,x,CY,0,gold,'z',40)}
// spool on rear side of rotor; string descends tangent to it
const spoolX=-.18, spoolY=CY, spoolZ=-.36, spoolR=.18;
cyl(scene,spoolR,spoolR,.24,spoolX,spoolY,spoolZ,gold,'z',48);
const stringGeo=new THREE.BufferGeometry();const stringMat=new THREE.LineBasicMaterial({color:0xffd166,linewidth:2});const string=new THREE.Line(stringGeo,stringMat);scene.add(string);
const massGroup=new THREE.Group();scene.add(massGroup);
box(massGroup,0,0,0,.38,.42,.34,massMat);box(massGroup,0,.02,.18,.22,.23,.015,gold);
cyl(massGroup,.045,.045,.12,0,.25,0,bright,'y',24);
// small label plate
box(scene,-2.0,2.9,0,.9,.42,.06,black);
const state={running:true,mode:'free',time:0,angle:0,omega:42*2*Math.PI/60,alpha:0,drop:0,phase:'free',history:[]};
function el(id){return document.getElementById(id)}
function params(){return {rpm:+el('rpm').value,m:+el('mass').value/1000,r:+el('radius').value/1000*1, I:+el('inertia').value/10000,tau:+el('tau').value/10000, speed:+el('speed').value/100}}
function refreshLabels(){const p=params();el('rpmval').textContent=p.rpm+' RPM';el('massval').textContent=Math.round(p.m*1000)+' g';el('radiusval').textContent=Math.round(p.r*1000)+' mm';el('ival').textContent=p.I.toFixed(4)+' kg m²';el('tauval').textContent=p.tau.toFixed(4)+' N m';el('speedval').textContent=p.speed.toFixed(2)+'×';el('designlabel').textContent=el('design').selectedOptions[0].text}
function setDesign(){const d=el('design').value;spokes.visible=d!=='disk';outer.visible=d==='disk';innerRing.visible=d!=='disk';torus.material=d==='rim'?gold:bright;innerTorus.visible=d==='precision';spokes.children.forEach(s=>s.scale.y=d==='precision'?.55:1);refreshLabels()}
function reset(){state.time=0;state.angle=0;state.drop=0;state.history=[];state.phase=state.mode==='fall'?'ready':'free';state.omega=state.mode==='fall'?0:params().rpm*2*Math.PI/60;state.alpha=0;state.running=false;el('start').textContent='▶ Start';el('status').textContent=state.phase==='ready'?'READY TO RELEASE':'PAUSED / READY';updateTelemetry(0);massGroup.position.set(spoolX,1.2,spoolZ);massGroup.visible=state.mode==='fall';}
function start(){if(state.mode==='fall'&&state.phase==='ready'){state.phase='falling';state.time=0;state.drop=0;state.omega=0}state.running=true;el('start').textContent='● Running';el('status').textContent=state.mode==='fall'?'FALLING-MASS EXPERIMENT':'AUTO ROTATION'}
function updateTelemetry(a){const w=state.omega;el('rpmout').textContent=(w*60/(2*Math.PI)).toFixed(1);el('wout').textContent=w.toFixed(2);el('aout').textContent=a.toFixed(2);el('tout').textContent=state.time.toFixed(2)}
el('mode').addEventListener('change',()=>{state.mode=el('mode').value;massGroup.visible=state.mode==='fall';reset();if(state.mode==='free')start();el('explain').textContent=state.mode==='fall'?'Release the hanging mass. The numerical model couples its downward acceleration to the wheel torque.':'The rotor turns freely. Change the design and orbit the apparatus to inspect its construction.'});
['rpm','mass','radius','inertia','tau','speed'].forEach(id=>el(id).addEventListener('input',()=>{refreshLabels();if(id==='rpm'&&state.mode==='free'&&state.time===0)state.omega=params().rpm*2*Math.PI/60}));
el('design').addEventListener('change',setDesign);
el('start').addEventListener('click',start);
el('stop').addEventListener('click',()=>{state.running=false;el('start').textContent='▶ Resume';el('status').textContent='PAUSED'});
el('reset').addEventListener('click',reset);
el('cam').addEventListener('click',()=>{camera.position.set(0,3.1,8.5);orbit.target.set(0,2,0);orbit.update()});
function updateString(){const top=new THREE.Vector3(spoolX+spoolR,spoolY,spoolZ-.13);const bottom=new THREE.Vector3(spoolX+spoolR,Math.max(.48,1.45-state.drop),spoolZ-.13);string.geometry.dispose();string.geometry=new THREE.BufferGeometry().setFromPoints([top,bottom]);massGroup.position.set(spoolX+spoolR,bottom.y-.25,spoolZ-.13)}
let prev=performance.now();
function animate(now){requestAnimationFrame(animate);const dt=Math.min((now-prev)/1000,.04);prev=now;const p=params();let alpha=0;
if(state.running){const ddt=dt*p.speed;state.time+=ddt;
 if(state.mode==='free'){if(p.tau>0){alpha=-p.tau/p.I;state.omega=Math.max(0,state.omega+alpha*ddt)}else{state.omega=p.rpm*2*Math.PI/60;alpha=0}}
 else if(state.phase==='falling'){
   alpha=(p.m*9.81*p.r-p.tau)/(p.I+p.m*p.r*p.r);if(alpha<0)alpha=0;
   const a=alpha*p.r;state.drop+=.5*a*ddt*ddt;state.omega+=alpha*ddt;
   if(state.drop>=1.15){state.drop=1.15;state.phase='coast';el('status').textContent='STRING DETACHED · COASTING'}
 }else if(state.phase==='coast'){alpha=-p.tau/p.I;state.omega=Math.max(0,state.omega+alpha*ddt);if(state.omega<=0){state.phase='stopped';state.running=false;el('status').textContent='ROTOR STOPPED';el('start').textContent='▶ Run again'}}
 state.angle+=state.omega*ddt;rotor.rotation.z=state.angle;
 if(state.mode==='fall'){massGroup.visible=true;updateString();if(state.phase==='falling'){el('explain').textContent='Mass falls; gravity supplies torque through the string.'}else if(state.phase==='coast'){el('explain').textContent='String has detached. Bearing friction removes rotational energy.'}else if(state.phase==='stopped'){el('explain').textContent='The rotor has stopped under the selected friction model.'}}
 state.history.push({t:state.time,w:state.omega});if(state.history.length>160)state.history.shift();
}else if(state.mode==='free'){rotor.rotation.z=state.angle;massGroup.visible=false}
updateTelemetry(alpha);
renderer.render(scene,camera);orbit.update();
}
function resize(){const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()}
new ResizeObserver(resize).observe(canvas);refreshLabels();setDesign();reset();start();requestAnimationFrame(animate);
</script></body></html>
"""
components.html(html, height=850, scrolling=False)
st.markdown("""
<div style="border:1px solid #263952;border-radius:14px;padding:16px 18px;background:#0b1320;margin-top:12px">
<b style="color:#d9ecff">Model notes</b><br>
<span style="color:#9fb4ce;font-size:13px">This is an interactive conceptual 3D apparatus. The falling-mass stage uses a simplified rigid-rotor model with no string slip. The scene is illustrative rather than a calibrated digital twin of a particular laboratory instrument.</span>
</div>
""", unsafe_allow_html=True)
