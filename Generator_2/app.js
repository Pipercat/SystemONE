// Einfacher Browser-Generator mit Three.js und STL-Export
(function(){
  const previewEl = document.getElementById('preview');
  const infoEl = document.getElementById('info');
  const typeSel = document.getElementById('type');
  const xInput = document.getElementById('x');
  const yInput = document.getElementById('y');
  const zInput = document.getElementById('z');
  const scaleInput = document.getElementById('scale');
  const previewBtn = document.getElementById('previewBtn');
  const downloadBtn = document.getElementById('downloadBtn');
  const zSection = document.getElementById('z-section');

  let scene, camera, renderer, controls, currentMesh;

  function initThree(){
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x091329);
    camera = new THREE.PerspectiveCamera(60, previewEl.clientWidth/previewEl.clientHeight, 0.1, 1000);
    camera.position.set(80,80,120);

    renderer = new THREE.WebGLRenderer({antialias:true});
    renderer.setSize(previewEl.clientWidth, previewEl.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio || 1);
    previewEl.innerHTML = '';
    previewEl.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.target.set(0,0,0);
    controls.update();

    const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.8);
    scene.add(hemi);
    const dir = new THREE.DirectionalLight(0xffffff, 0.8);
    dir.position.set(100,100,100);
    scene.add(dir);

    window.addEventListener('resize', onResize);

    animate();
  }

  function onResize(){
    if(!renderer) return;
    camera.aspect = previewEl.clientWidth/previewEl.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(previewEl.clientWidth, previewEl.clientHeight);
  }

  function clearMesh(){
    if(currentMesh){
      scene.remove(currentMesh);
      currentMesh.geometry.dispose();
      if(Array.isArray(currentMesh.material)) currentMesh.material.forEach(m=>m.dispose()); else currentMesh.material.dispose();
      currentMesh = null;
    }
  }

  function buildBin(x,y,z,scale){
    // simple box with wall thickness and chamfer can be added later
    const wx = x * scale;
    const wy = y * scale;
    const wz = z * scale;

    const outer = new THREE.BoxGeometry(wx, wz, wy); // note: swap axes for better orientation
    const material = new THREE.MeshStandardMaterial({color:0x4fb06a, metalness:0.1, roughness:0.6});
    const mesh = new THREE.Mesh(outer, material);
    mesh.rotation.x = -Math.PI/2; // lay flat so height points up
    return mesh;
  }

  function buildBaseplate(x,y,scale){
    const wx = x * scale;
    const wy = y * scale;
    const thickness = scale * 0.5;
    const geom = new THREE.BoxGeometry(wx, thickness, wy);
    const mat = new THREE.MeshStandardMaterial({color:0x6ca0ff, metalness:0.05, roughness:0.7});
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.y = -thickness/2; // keep top at y=0
    return mesh;
  }

  function updatePreview(){
    if(!scene) initThree();
    clearMesh();
    const type = typeSel.value;
    const x = Math.max(1, parseInt(xInput.value||1));
    const y = Math.max(1, parseInt(yInput.value||1));
    const z = Math.max(1, parseInt(zInput.value||1));
    const scale = Math.max(1, parseFloat(scaleInput.value||20));

    if(type==='bin'){
      currentMesh = buildBin(x,y,z,scale);
      infoEl.textContent = `Box: ${x}×${y}×${z} Einheiten @ ${scale} mm`; 
    } else {
      currentMesh = buildBaseplate(x,y,scale);
      infoEl.textContent = `Baseplate: ${x}×${y} Einheiten @ ${scale} mm`;
    }

    scene.add(currentMesh);
    focusObject(currentMesh);
  }

  function focusObject(obj){
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI/180);
    let dist = Math.abs(maxDim / 2 / Math.tan(fov / 2));
    dist *= 1.6; // padding
    camera.position.set(center.x + dist, center.y + dist, center.z + dist);
    camera.lookAt(center);
    controls.target.copy(center);
    controls.update();
  }

  function animate(){
    requestAnimationFrame(animate);
    if(renderer) renderer.render(scene, camera);
  }

  function downloadSTL(){
    if(!currentMesh) return alert('Bitte zuerst Vorschau erstellen.');
    const exporter = new THREE.STLExporter();
    const res = exporter.parse(currentMesh, {binary:false});
    const blob = new Blob([res], {type: 'text/plain'});
    const now = new Date().toISOString().replace(/[:.]/g,'-');
    const type = typeSel.value;
    const filename = `${type}_${now}.stl`;
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  // UI wiring
  typeSel.addEventListener('change', ()=>{
    if(typeSel.value==='base') zSection.style.display = 'none'; else zSection.style.display = 'block';
    updatePreview();
  });

  previewBtn.addEventListener('click', (e)=>{ e.preventDefault(); updatePreview(); });
  downloadBtn.addEventListener('click', (e)=>{ e.preventDefault(); downloadSTL(); });

  // init
  initThree();
  updatePreview();
})();