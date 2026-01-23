import * as THREE from "./vendor/three.module.js";
import { OrbitControls } from "./vendor/OrbitControls.js";
import { STLLoader } from "./vendor/STLLoader.js";

window.__JS_BOOT_OK = true;
const jsStatus = document.getElementById("jsStatusText");
if (jsStatus) jsStatus.textContent = "✅ app.js läuft (offline). Three.js wird initialisiert…";

const $ = (id) => document.getElementById(id);
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const num = (id, fallback = 0) => {
  const el = $(id);
  if (!el) return fallback;
  const v = Number(String(el.value).replace(",", "."));
  return Number.isFinite(v) ? v : fallback;
};

/* ---------- Views ---------- */
function setActiveNav(view) {
  document.querySelectorAll(".nav .item").forEach((el) => el.classList.remove("active"));
  const it = document.querySelector(`.nav .item[data-view="${view}"]`);
  if (it) it.classList.add("active");
}

function showView(view) {
  ["generator", "presets", "history", "about"].forEach((v) => {
    const el = $(`view-${v}`);
    if (el) el.classList.toggle("hidden", v !== view);
  });
  setActiveNav(view);

  const title = { generator:"Generator", presets:"Presets", history:"Verlauf", about:"Roadmap" }[view] || "Generator";
  if ($("viewTitle")) $("viewTitle").textContent = title;
}

/* ---------- Storage ---------- */
const LS = {
  presetsKey: "gf_v3_presets",
  histKey: "gf_v3_history",
  load(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key) || "") ?? fallback; }
    catch { return fallback; }
  },
  save(key, data) { localStorage.setItem(key, JSON.stringify(data)); }
};
const getPresets = () => LS.load(LS.presetsKey, []);
const getHistory = () => LS.load(LS.histKey, []);
function updateBadges() {
  if ($("presetCount")) $("presetCount").textContent = String(getPresets().length);
  if ($("histCount")) $("histCount").textContent = String(getHistory().length);
}

/* ---------- Three setup ---------- */
const viewerEl = $("viewer");
if (!viewerEl) throw new Error("#viewer not found");

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(viewerEl.clientWidth, viewerEl.clientHeight);
renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
renderer.domElement.style.width = "100%";
renderer.domElement.style.height = "100%";
viewerEl.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(55, viewerEl.clientWidth / viewerEl.clientHeight, 0.1, 5000);
camera.position.set(220, 180, 220);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.update();

scene.add(new THREE.AmbientLight(0xffffff, 0.55));
const key = new THREE.DirectionalLight(0xffffff, 0.85);
key.position.set(200, 300, 180);
scene.add(key);

const grid = new THREE.GridHelper(800, 40, 0x2b3a5a, 0x1f2b47);
grid.position.y = -40;
scene.add(grid);

const axes = new THREE.AxesHelper(120);
axes.position.y = -40;
scene.add(axes);

function fitCameraToObject(object, offset = 1.45) {
  const box = new THREE.Box3().setFromObject(object);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);

  const maxDim = Math.max(size.x, size.y, size.z);
  const fov = (camera.fov * Math.PI) / 180;
  const dist = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * offset;

  camera.position.set(center.x + dist, center.y + dist * 0.65, center.z + dist);
  camera.near = Math.max(0.1, maxDim / 200);
  camera.far = Math.max(2000, maxDim * 20);
  camera.updateProjectionMatrix();

  controls.target.copy(center);
  controls.update();
}

let previewMesh = null;

function setKPI(geometry, label) {
  geometry.computeBoundingBox();
  const bb = geometry.boundingBox;
  const size = new THREE.Vector3();
  bb.getSize(size);

  if ($("kpiType")) $("kpiType").textContent = label;
  if ($("kpiSize")) $("kpiSize").textContent = `${Math.round(size.x)}×${Math.round(size.z)}×${Math.round(size.y)} mm`;

  const tri = geometry.toNonIndexed().getAttribute("position").count / 3;
  if ($("kpiTri")) $("kpiTri").textContent = String(Math.round(tri));
}

function setMesh(geometry, label) {
  if (previewMesh) {
    scene.remove(previewMesh);
    previewMesh.geometry.dispose();
    previewMesh.material.dispose();
  }

  geometry.computeVertexNormals();
  geometry.computeBoundingBox();

  const mat = new THREE.MeshStandardMaterial({
    color: 0x3b82f6,
    roughness: 0.45,
    metalness: 0.10,
  });

  previewMesh = new THREE.Mesh(geometry, mat);

  const bb = geometry.boundingBox;
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  bb.getSize(size);
  bb.getCenter(center);

  previewMesh.position.sub(center);
  previewMesh.position.y += size.y / 2 - 40;

  scene.add(previewMesh);
  fitCameraToObject(previewMesh);
  setKPI(geometry, label);
}

/* ---------- Geometry: gridfinity-like preview ---------- */
function mergeGeometries(geoms) {
  const merged = new THREE.BufferGeometry();
  const positions = [];
  const normals = [];
  const indices = [];
  let off = 0;

  for (const g0 of geoms) {
    const g = g0.toNonIndexed();
    const pos = g.getAttribute("position");
    const nor = g.getAttribute("normal");

    for (let i = 0; i < pos.count; i++) {
      positions.push(pos.getX(i), pos.getY(i), pos.getZ(i));
      normals.push(nor.getX(i), nor.getY(i), nor.getZ(i));
      indices.push(off++);
    }
  }

  merged.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  merged.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  merged.setIndex(indices);
  return merged;
}

function buildBin({ mm, x, y, z, wall }) {
  const outerW = x * mm;
  const outerD = y * mm;
  const unitH = mm / 7;
  const outerH = z * unitH;

  const bottom = wall * 1.2;
  const innerW = Math.max(outerW - 2 * wall, wall);
  const innerD = Math.max(outerD - 2 * wall, wall);
  const innerH = Math.max(outerH - bottom - wall * 0.2, wall);

  const meshes = [];

  // floor
  { const m = new THREE.Mesh(new THREE.BoxGeometry(outerW, bottom, outerD));
    m.position.set(0, -(outerH / 2) + bottom / 2, 0);
    meshes.push(m);
  }

  // walls
  { const m = new THREE.Mesh(new THREE.BoxGeometry(wall, outerH, outerD));
    m.position.set(-(outerW / 2) + wall / 2, 0, 0);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(wall, outerH, outerD));
    m.position.set((outerW / 2) - wall / 2, 0, 0);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(outerW - 2 * wall, outerH, wall));
    m.position.set(0, 0, -(outerD / 2) + wall / 2);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(outerW - 2 * wall, outerH, wall));
    m.position.set(0, 0, (outerD / 2) - wall / 2);
    meshes.push(m);
  }

  // rim
  const rimT = Math.max(0.8, wall * 0.8);
  const rimH = Math.max(1.2, wall * 0.9);
  const rimY = -(outerH / 2) + bottom + innerH - rimH / 2;

  { const m = new THREE.Mesh(new THREE.BoxGeometry(rimT, rimH, innerD));
    m.position.set(-(innerW / 2) + rimT / 2, rimY, 0);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(rimT, rimH, innerD));
    m.position.set((innerW / 2) - rimT / 2, rimY, 0);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(innerW, rimH, rimT));
    m.position.set(0, rimY, -(innerD / 2) + rimT / 2);
    meshes.push(m);
  }
  { const m = new THREE.Mesh(new THREE.BoxGeometry(innerW, rimH, rimT));
    m.position.set(0, rimY, (innerD / 2) - rimT / 2);
    meshes.push(m);
  }

  // foot
  { const footH = 2.2, inset = 2.4;
    const m = new THREE.Mesh(new THREE.BoxGeometry(Math.max(1, outerW - inset * 2), footH, Math.max(1, outerD - inset * 2)));
    m.position.set(0, -(outerH / 2) - footH / 2, 0);
    meshes.push(m);
  }

  const geoms = meshes.map((m) => {
    m.updateMatrix();
    return m.geometry.clone().applyMatrix4(m.matrix);
  });

  const merged = mergeGeometries(geoms);
  merged.computeVertexNormals();
  return merged;
}

function buildBaseplate({ mm, x, y, style, magnet, quality }) {
  const w = x * mm;
  const d = y * mm;
  const thickness = style === 0 ? 6 : style === 1 ? 10 : 6;

  const meshes = [];
  meshes.push(new THREE.Mesh(new THREE.BoxGeometry(w, thickness, d)));

  // grid lines
  const lineT = 0.8;
  const lineH = Math.min(1.4, thickness * 0.25);

  for (let i = 1; i < x; i++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(lineT, lineH, d));
    m.position.set(-(w / 2) + i * mm, (thickness / 2) - lineH / 2, 0);
    meshes.push(m);
  }
  for (let j = 1; j < y; j++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, lineH, lineT));
    m.position.set(0, (thickness / 2) - lineH / 2, -(d / 2) + j * mm);
    meshes.push(m);
  }

  if (magnet === 1) {
    const segs = quality === "high" ? 48 : quality === "low" ? 16 : 28;
    const holeR = 3.2, holeH = 1.2;

    for (let gx = 0; gx < x; gx++) {
      for (let gy = 0; gy < y; gy++) {
        const cx = -(w / 2) + gx * mm + mm / 2;
        const cz = -(d / 2) + gy * mm + mm / 2;
        const cyl = new THREE.Mesh(new THREE.CylinderGeometry(holeR, holeR, holeH, segs));
        cyl.position.set(cx, -(thickness / 2) + holeH / 2, cz);
        meshes.push(cyl);
      }
    }
  }

  const geoms = meshes.map((m) => {
    m.updateMatrix();
    return m.geometry.clone().applyMatrix4(m.matrix);
  });

  const merged = mergeGeometries(geoms);
  merged.computeVertexNormals();
  return merged;
}

/* ---------- STL export ---------- */
function geometryToAsciiSTL(geom) {
  const g = geom.toNonIndexed();
  const pos = g.getAttribute("position");
  const nor = g.getAttribute("normal");

  let out = "solid gridfinity_v3\n";
  for (let i = 0; i < pos.count; i += 3) {
    const nx = nor.getX(i), ny = nor.getY(i), nz = nor.getZ(i);
    out += `  facet normal ${nx} ${ny} ${nz}\n`;
    out += "    outer loop\n";
    for (let j = 0; j < 3; j++) {
      out += `      vertex ${pos.getX(i + j)} ${pos.getY(i + j)} ${pos.getZ(i + j)}\n`;
    }
    out += "    endloop\n";
    out += "  endfacet\n";
  }
  out += "endsolid gridfinity_v3\n";
  return out;
}

function downloadTextFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

/* ---------- State + Summary ---------- */
function getState() {
  return {
    type: $("typeSelect")?.value || "bin",
    mmPerUnit: clamp(num("mmPerUnit", 42), 5, 200),
    bin: {
      x: clamp(num("bin_x", 2), 1, 50),
      y: clamp(num("bin_y", 2), 1, 50),
      z: clamp(num("bin_z", 6), 1, 50),
      wall: clamp(num("bin_wall", 1.6), 0.8, 5),
    },
    baseplate: {
      x: clamp(num("bp_x", 4), 1, 200),
      y: clamp(num("bp_y", 6), 1, 200),
      style: Number($("bp_style")?.value ?? 0),
      magnet: Number($("bp_magnet")?.value ?? 0),
    },
    adv: {
      quality: $("adv_quality")?.value ?? "med",
    }
  };
}

function setSummary(state) {
  if (!$("summary")) return;
  if (state.type === "baseplate") {
    $("summary").value = `V3 | BASEPLATE | gridx=${state.baseplate.x} gridy=${state.baseplate.y} mm=${state.mmPerUnit} style=${state.baseplate.style} magnet=${state.baseplate.magnet}`;
  } else {
    $("summary").value = `V3 | BIN | gridx=${state.bin.x} gridy=${state.bin.y} gridz=${state.bin.z} mm=${state.mmPerUnit} wall=${state.bin.wall}`;
  }
}

function buildFromState(state) {
  if (state.type === "baseplate") {
    return buildBaseplate({
      mm: state.mmPerUnit,
      x: state.baseplate.x,
      y: state.baseplate.y,
      style: state.baseplate.style,
      magnet: state.baseplate.magnet,
      quality: state.adv.quality,
    });
  }
  return buildBin({
    mm: state.mmPerUnit,
    x: state.bin.x,
    y: state.bin.y,
    z: state.bin.z,
    wall: state.bin.wall,
  });
}

function updatePreview() {
  const state = getState();
  const geom = buildFromState(state);
  setMesh(geom, state.type === "baseplate" ? "Baseplate (Preview)" : "Bin (Preview)");
  setSummary(state);
}

function updatePreviewDebounced() {
  clearTimeout(window.__pv);
  window.__pv = setTimeout(updatePreview, 120);
}

function onTypeSelect() {
  const type = $("typeSelect").value;
  switchTab(type === "baseplate" ? "baseplate" : "bin");
}

function switchTab(tab) {
  ["bin","baseplate","advanced"].forEach((t) => {
    $(`panel-${t}`)?.classList.toggle("hidden", t !== tab);
    $(`tab-${t}`)?.classList.toggle("active", t === tab);
  });

  if (tab === "baseplate") $("typeSelect").value = "baseplate";
  if (tab === "bin") $("typeSelect").value = "bin";

  updatePreview();
}

/* ---------- STL Import ---------- */
async function loadSTLFromFile() {
  const input = $("stlFile");
  if (!input?.files || input.files.length === 0) return;

  const file = input.files[0];
  const buf = await file.arrayBuffer();
  const loader = new STLLoader();
  const geom = loader.parse(buf);

  setMesh(geom, "STL Import (1:1)");
  if ($("summary")) $("summary").value = `V3 | STL IMPORT | file="${file.name}"`;
}

/* ---------- Minimal presets/history just to prove it works ---------- */
function savePreset() {
  const state = getState();
  const name = prompt("Preset Name?", state.type === "baseplate"
    ? `Baseplate ${state.baseplate.x}x${state.baseplate.y}`
    : `Bin ${state.bin.x}x${state.bin.y}x${state.bin.z}`
  );
  if (!name) return;

  const p = getPresets();
  p.unshift({ id: Date.now(), name, state });
  LS.save(LS.presetsKey, p.slice(0, 60));
  updateBadges();
  renderPresets();
}

function addHistory() {
  const h = getHistory();
  h.unshift({ id: Date.now(), at: new Date().toISOString(), summary: $("summary")?.value || "" });
  LS.save(LS.histKey, h.slice(0, 80));
  updateBadges();
  renderHistory();
}

function exportState() {
  const state = getState();
  downloadTextFile("gridfinity_v3_state.json", JSON.stringify(state, null, 2), "application/json");
  addHistory();
}

function downloadSTL() {
  if (!previewMesh) return;

  const geom = previewMesh.geometry.clone();
  previewMesh.updateMatrixWorld(true);
  geom.applyMatrix4(previewMesh.matrixWorld);
  geom.computeVertexNormals();

  const stl = geometryToAsciiSTL(geom);
  downloadTextFile(`gridfinity_v3_${getState().type}.stl`, stl, "model/stl");
  addHistory();
}

/* ---------- Render lists ---------- */
function renderPresets() {
  const list = $("presetList");
  if (!list) return;
  const p = getPresets();
  list.innerHTML = p.length ? "" : `<div class="sidecard"><p>Keine Presets gespeichert.</p></div>`;
  for (const it of p) {
    const el = document.createElement("div");
    el.className = "sidecard";
    el.innerHTML = `<h3>${it.name}</h3><p class="sub mono">${JSON.stringify(it.state)}</p>`;
    list.appendChild(el);
  }
}
function renderHistory() {
  const list = $("historyList");
  if (!list) return;
  const h = getHistory();
  list.innerHTML = h.length ? "" : `<div class="sidecard"><p>Kein Verlauf vorhanden.</p></div>`;
  for (const it of h) {
    const el = document.createElement("div");
    el.className = "sidecard";
    el.innerHTML = `<h3>${it.at}</h3><p class="sub mono">${it.summary}</p>`;
    list.appendChild(el);
  }
}

/* ---------- Public API ---------- */
window.UI = {
  setView: (v) => { showView(v); if (v === "presets") renderPresets(); if (v === "history") renderHistory(); },
  switchTab,
  onTypeSelect,
  updatePreview,
  updatePreviewDebounced,
  loadSTLFromFile,
  downloadSTL,
  savePreset,
  addHistory,
  exportState,
  defaults: () => { $("typeSelect").value="bin"; switchTab("bin"); updatePreview(); },
  copySummary: () => { $("summary")?.select(); document.execCommand?.("copy"); }
};

/* ---------- Init ---------- */
updateBadges();
showView("generator");
switchTab("bin");
updatePreview();

if (jsStatus) jsStatus.textContent = "✅ Three.js aktiv (offline). Vorschau wird gerendert.";

window.addEventListener("resize", () => {
  renderer.setSize(viewerEl.clientWidth, viewerEl.clientHeight);
  camera.aspect = viewerEl.clientWidth / viewerEl.clientHeight;
  camera.updateProjectionMatrix();
});

(function loop(){
  requestAnimationFrame(loop);
  controls.update();
  renderer.render(scene, camera);
})();
