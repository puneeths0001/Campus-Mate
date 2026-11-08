# app.py - Home page of Campus Mate (run with: streamlit run app.py)
import streamlit as st
import streamlit.components.v1 as components
from theme import apply_theme

st.set_page_config(page_title="Campus Mate", page_icon="🎓", layout="wide")
apply_theme()

# 3D hero card. Three.js draws soft "clay" shapes that squish and giggle when you touch them.
HERO = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap');
  html, body { margin:0; background:transparent; font-family:'Inter',sans-serif; }
  .card { position:relative; height:330px; margin:4px; border-radius:24px; overflow:hidden;
          background:radial-gradient(circle at 78% 25%, rgba(124,92,255,.30), transparent 55%), #17171D; border:1px solid rgba(255,255,255,.08);
          }
  canvas { position:absolute; inset:0; width:100%; height:100%; }
  .txt { position:relative; z-index:2; padding:46px 44px; color:#fff; max-width:470px; pointer-events:none; }
  h1 { font-size:clamp(30px,5vw,46px); margin:0; font-weight:800; line-height:1.05; }
  p  { font-size:17px; color:#9A9AA5; margin:14px 0 0; font-weight:600; }
  .hint { margin-top:22px; display:inline-block; background:#7C5CFF; color:#fff; font-weight:600;
          padding:9px 20px; border-radius:999px; box-shadow:0 8px 24px rgba(124,92,255,.45); }
</style>
<div class="card"><canvas id="c"></canvas>
  <div class="txt"><h1>Hi there! 👋<br>Welcome to Campus Mate</h1>
  <p>Safety, study, money and scam protection for college life.</p>
  <span class="hint">Poke the shapes, they giggle</span></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({canvas, alpha:true, antialias:true});
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100); camera.position.z = 9;
scene.add(new THREE.AmbientLight(0xffffff, 0.85));
const sun = new THREE.DirectionalLight(0xffffff, 0.9); sun.position.set(3, 5, 6); scene.add(sun);

// Clay shapes: [geometry, color, x, y]
const defs = [
  [new THREE.SphereGeometry(1.25, 48, 48), 0x7C5CFF, 0.0, 0.2],
  [new THREE.SphereGeometry(0.8, 48, 48), 0x3DDC97, -1.9, -0.9],
  [new THREE.SphereGeometry(0.6, 48, 48), 0x4B3FB5, 1.9, -1.0],
  [new THREE.TorusGeometry(0.55, 0.25, 32, 64), 0xE8E8F0, 1.7, 1.3],
];
const blobs = defs.map(([g, color, x, y], i) => {
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({color, roughness:0.45, metalness:0.05}));
  m.position.set(x, y, 0); m.userData = {x, y, i, kick:0}; scene.add(m); return m;
});
const group = new THREE.Group(); blobs.forEach(b => group.add(b)); scene.add(group);

const ray = new THREE.Raycaster(), mouse = new THREE.Vector2();
function poke(e) {                       // touching a shape makes it giggle
  const r = canvas.getBoundingClientRect();
  mouse.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
  ray.setFromCamera(mouse, camera);
  ray.intersectObjects(blobs).forEach(h => h.object.userData.kick = 1);
}
canvas.addEventListener('pointerdown', poke);
canvas.addEventListener('pointermove', poke);

function resize() {
  const r = canvas.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false);
  camera.aspect = r.width / r.height; camera.updateProjectionMatrix();
  group.position.x = r.width > 700 ? 2.6 : 0; group.position.y = r.width > 700 ? 0 : -1.2;
}
window.addEventListener('resize', resize); resize();

const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  blobs.forEach(b => {
    const u = b.userData;
    b.position.y = u.y + Math.sin(t * 1.2 + u.i) * 0.18;           // floating
    const s = Math.sin(t * 16) * u.kick * 0.3;                     // giggle squish
    b.scale.set(1 + s + Math.sin(t + u.i) * 0.03, 1 - s - Math.sin(t + u.i) * 0.03, 1 + s);
    b.rotation.z = Math.sin(t * 18) * u.kick * 0.25;
    if (u.i === 3) b.rotation.x += 0.02;
    u.kick *= 0.95;
  });
  renderer.render(scene, camera);
}
animate();
</script>
"""
components.html(HERO, height=350)

st.markdown("""
<style>
.bento { display:grid; grid-template-columns:repeat(4,1fr); grid-template-rows:repeat(3,minmax(190px,auto)); gap:16px; margin-top:8px; }
.tile { position:relative; overflow:hidden; background:#17171D; border:1px solid rgba(255,255,255,.08); border-radius:24px;
        padding:24px; display:flex; flex-direction:column; transition:transform .2s ease, border-color .2s ease; }
.tile:hover { transform:translateY(-4px); border-color:rgba(255,255,255,.22); }
.tile::before { content:""; position:absolute; top:-90px; right:-90px; width:260px; height:260px; border-radius:50%;
        background:radial-gradient(circle, var(--accent), transparent 70%); opacity:.22; pointer-events:none; }
.violet { --accent:#7C5CFF; } .mint { --accent:#3DDC97; }
.t-hero { grid-column:1 / 3; grid-row:1 / 3; } .t-scam { grid-column:3 / 5; grid-row:1; } .t-flow { grid-column:3 / 5; grid-row:2; }
.tag { color:#9A9AA5; font-size:13px; font-weight:500; margin-bottom:10px; }
.th { color:#fff; font-size:20px; font-weight:700; line-height:1.2; letter-spacing:-.02em; }
.t-hero .th { font-size:30px; }
.tp { color:#9A9AA5; font-size:14px; line-height:1.5; margin-top:8px; }
.spacer { flex:1; }
/* hero: mini map */
.map { position:relative; margin-top:18px; flex:1; min-height:150px; border-radius:16px; border:1px solid rgba(255,255,255,.08);
       background-color:#0F0F14; background-image:linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
       background-size:32px 32px; }
.ping { position:absolute; left:58%; top:48%; width:14px; height:14px; border-radius:50%; background:#3DDC97; }
.ping::after { content:""; position:absolute; inset:-10px; border-radius:50%; border:2px solid #3DDC97; animation:ping 1.8s ease-out infinite; }
@keyframes ping { from { transform:scale(.4); opacity:.9; } to { transform:scale(1.6); opacity:0; } }
.chip { display:inline-block; font-size:12px; font-weight:600; color:#fff; background:rgba(255,255,255,.08); padding:5px 10px; border-radius:999px; }
.map .chip { position:absolute; left:14px; bottom:14px; }
/* scam: risk meter */
.meter { display:flex; align-items:center; gap:12px; margin-top:16px; }
.bar { flex:1; height:8px; background:rgba(255,255,255,.08); border-radius:99px; overflow:hidden; }
.bar i { display:block; height:100%; width:92%; background:linear-gradient(90deg,#7C5CFF,#FF5C7A); border-radius:99px; }
.meter b { color:#fff; font-size:13px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
/* flowchart: mini diagram */
.flow { display:flex; align-items:center; gap:8px; margin-top:16px; }
.flow b { color:#fff; font-size:13px; font-weight:600; padding:8px 12px; border-radius:10px; background:rgba(61,220,151,.12); border:1px solid rgba(61,220,151,.35); }
.flow u { flex:0 0 22px; height:2px; background:#3DDC97; opacity:.6; }
/* stat + bars */
.stat { color:#fff; font-size:48px; font-weight:700; letter-spacing:-.03em; line-height:1; }
.bars { display:flex; align-items:flex-end; gap:7px; height:64px; margin-top:14px; }
.bars i { flex:1; background:linear-gradient(180deg,#3DDC97,rgba(61,220,151,.25)); border-radius:6px; }
.ico { font-size:30px; margin-bottom:12px; }
.note { align-self:center; padding:0 8px; color:#9A9AA5; font-size:14px; line-height:1.5; }
.note b { color:#fff; display:block; font-size:18px; margin-bottom:4px; }
@media (prefers-reduced-motion: reduce) { .ping::after { animation:none; } }
@media (max-width:900px) {
  .bento { grid-template-columns:1fr; grid-template-rows:none; }
  .t-hero, .t-scam, .t-flow { grid-column:auto; grid-row:auto; }
}
</style>
<div class="bento">
<div class="tile t-hero mint"><div class="tag">🚨 Safety SOS</div><div class="th">Say “help”. Your parents see where you are.</div><div class="tp">One tap or one word sends your live location to their phone.</div><div class="map"><span class="ping"></span><span class="chip">Live location · updates every 5 min</span></div></div>
<div class="tile t-scam violet"><div class="tag">🛡️ Scam detector</div><div class="th">Check before you click.</div><div class="tp">Paste a link, email or internship offer and get a risk score with reasons.</div><div class="spacer"></div><div class="meter"><div class="bar"><i></i></div><b>High risk</b></div><div class="chips"><span class="chip">Registration fee</span><span class="chip">Fake domain</span><span class="chip">Urgency</span></div></div>
<div class="tile t-flow mint"><div class="tag">🧠 Notes to flowchart</div><div class="th">Messy notes in. Clear diagram out.</div><div class="tp">Gemini turns your notes into a flowchart for fast revision.</div><div class="spacer"></div><div class="flow"><b>Notes</b><u></u><b>Key ideas</b><u></u><b>Flowchart</b></div></div>
<div class="tile violet"><div class="tag">📊 CGPA planner</div><div class="stat">8.4</div><div class="spacer"></div><div class="th" style="font-size:16px">See which subject costs you the most.</div><div class="tp" style="margin-top:4px">Sample SGPA</div></div>
<div class="tile mint"><div class="tag">💸 Expenses</div><div class="th" style="font-size:16px">Know where money goes.</div><div class="bars"><i style="height:45%"></i><i style="height:80%"></i><i style="height:35%"></i><i style="height:95%"></i><i style="height:60%"></i></div><div class="tp" style="margin-top:10px">Alerts when you cross your limit.</div></div>
<div class="tile violet"><div class="ico">⏰</div><div class="th" style="font-size:16px">Say it once.</div><div class="tp">Speak a deadline. We keep it and warn you before it is due.</div></div>
<div class="note"><b>Six tools. One app.</b>Open any of them from the menu on the left.</div>
</div>
""", unsafe_allow_html=True)
