# app.py - Home page of Campus Mate (run with: streamlit run app.py)
import streamlit as st
import streamlit.components.v1 as components
from theme import apply_theme

st.set_page_config(page_title="Campus Mate", page_icon="🎓", layout="wide")
apply_theme()

# 3D hero card. Three.js draws soft "clay" shapes that squish and giggle when you touch them.
HERO = """
<style>
  html, body { margin:0; background:transparent; font-family:'Nunito',sans-serif; }
  .card { position:relative; height:330px; margin:4px; border-radius:32px; overflow:hidden;
          background:linear-gradient(120deg,#ffffff 0%,#EADCFF 55%,#FFD6EC 100%);
          box-shadow:0 14px 32px rgba(124,92,252,.22), inset 0 3px 8px #fff; }
  canvas { position:absolute; inset:0; width:100%; height:100%; }
  .txt { position:relative; z-index:2; padding:46px 44px; color:#2B2350; max-width:470px; pointer-events:none; }
  h1 { font-size:clamp(30px,5vw,46px); margin:0; font-weight:800; line-height:1.05; }
  p  { font-size:17px; color:#5a4f8a; margin:14px 0 0; font-weight:600; }
  .hint { margin-top:22px; display:inline-block; background:#7C5CFC; color:#fff; font-weight:800;
          padding:9px 20px; border-radius:999px; box-shadow:0 8px 16px rgba(124,92,252,.4); }
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
  [new THREE.SphereGeometry(1.25, 48, 48), 0x9B7FFF, 0.0, 0.2],
  [new THREE.SphereGeometry(0.8, 48, 48), 0xFFA9C8, -1.9, -0.9],
  [new THREE.SphereGeometry(0.6, 48, 48), 0x7FE3C1, 1.9, -1.0],
  [new THREE.TorusGeometry(0.55, 0.25, 32, 64), 0xFFC98A, 1.7, 1.3],
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

st.subheader("What Campus Mate does")
# (icon, title, text, card color)
features = [
    ("🚨", "Safety SOS", "Say “help” and your parents get your live location.", "#FFE1E8"),
    ("⏰", "Voice reminders", "Speak a deadline once. We remind you before it hits.", "#FFF1CC"),
    ("💸", "Expense tracker", "See where your money goes and when you cross your limit.", "#D8F5E8"),
    ("🛡️", "Scam detector", "Paste a link, email or internship offer and check the risk.", "#DCEBFF"),
    ("📊", "CGPA planner", "Find which subjects pull your CGPA down and fix them.", "#EADCFF"),
    ("🧠", "Notes to flowchart", "Turn messy notes into a diagram for fast revision.", "#FFDDF0"),
]
for row in (features[:3], features[3:]):
    cols = st.columns(3)
    for col, (icon, title, text, color) in zip(cols, row):
        col.markdown(
            f'<div class="cm-card" style="background:linear-gradient(135deg,rgba(255,255,255,.7),{color})">'
            f'<div class="ico">{icon}</div><h3>{title}</h3><p>{text}</p></div>',
            unsafe_allow_html=True)
    st.write("")
st.caption("Open each feature from the purple menu on the left.")
