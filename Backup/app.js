const UI = (() => {
  const TOOLS = {
    perplexing: {
      name: "Perplexing Labs",
      // Web UI wrapper; browser-only use case
      urlBin: "https://gridfinity.perplexinglabs.com/",
      urlBaseplate: "https://gridfinity.perplexinglabs.com/",
      iframeLikely: false, // viele Tools blocken iFrame per headers
    },
    webopenscad: {
      name: "Web OpenSCAD Customizer",
      urlBin: "https://vector76.github.io/Web_OpenSCAD_Customizer/gridfinity_bins.html",
      urlBaseplate: "https://vector76.github.io/Web_OpenSCAD_Customizer/gridfinity_bins.html",
      iframeLikely: true,
    },
    gridfinitygen: {
      name: "gridfinitygenerator.com",
      urlBin: "https://gridfinitygenerator.com/en/box",
      urlBaseplate: "https://gridfinitygenerator.com/en/baseplate",
      iframeLikely: false,
    }
  };

  const state = {
    view: "generator",
    tab: "bin",
    history: loadHistory(),
  };

  function $(id){ return document.getElementById(id); }
  function val(id){ return $(id)?.value ?? ""; }
  function num(id){ return Number(val(id) || 0); }

  function toast(msg){
    const t = $("toast");
    $("toastText").textContent = msg;
    t.classList.add("show");
    clearTimeout(toast._tm);
    toast._tm = setTimeout(()=>t.classList.remove("show"), 1400);
  }

  function setView(view){
    state.view = view;
    ["generator","history","about"].forEach(v=>{
      $("view-"+v).classList.toggle("hidden", v!==view);
    });
    document.querySelectorAll(".nav .item").forEach(el=>{
      el.classList.toggle("active", el.dataset.view === view);
    });
    if(view==="generator"){
      $("viewTitle").textContent="Generator";
      $("viewSubtitle").textContent="SmartSorter Dark UI · kostenloser Online-Renderer";
    } else if(view==="history"){
      $("viewTitle").textContent="Verlauf";
      $("viewSubtitle").textContent="Gespeicherte Parameter (localStorage)";
      renderHistory();
    } else {
      $("viewTitle").textContent="Info";
      $("viewSubtitle").textContent="Welche Tools? Was ist reproduzierbar?";
    }
  }

  function switchTab(tab){
    state.tab = tab;
    $("tab-bin").classList.toggle("active", tab==="bin");
    $("tab-baseplate").classList.toggle("active", tab==="baseplate");

    $("panel-bin").classList.toggle("hidden", tab!=="bin");
    $("panel-baseplate").classList.toggle("hidden", tab!=="baseplate");

    updatePreview();
  }

  function defaults(){
    $("toolSelect").value = "perplexing";

    $("bin_x").value=2; $("bin_y").value=2; $("bin_z").value=6;
    $("bin_divx").value=1; $("bin_divy").value=1;

    $("bp_x").value=4; $("bp_y").value=6;
    $("bp_style").value="0";
    $("bp_magnet").value="0";

    updatePreview();
    toast("Defaults gesetzt");
  }

  function currentTool(){
    const key = val("toolSelect");
    return { key, ...(TOOLS[key] || TOOLS.perplexing) };
  }

  function buildSummary(){
    const tool = currentTool();
    if(state.tab === "bin"){
      const x=num("bin_x"), y=num("bin_y"), z=num("bin_z");
      const dx=num("bin_divx"), dy=num("bin_divy");
      return `${tool.name} | Box | gridx=${x} gridy=${y} gridz=${z} divx=${dx} divy=${dy}`;
    } else {
      const x=num("bp_x"), y=num("bp_y");
      const style=val("bp_style"), mag=val("bp_magnet");
      return `${tool.name} | Baseplate | gridx=${x} gridy=${y} style_plate=${style} enable_magnet=${mag}`;
    }
  }

  function buildLink(){
    const tool = currentTool();
    return (state.tab === "bin") ? tool.urlBin : tool.urlBaseplate;
  }

  function updatePreview(){
    const tool = currentTool();
    const link = buildLink();

    // badge
    if(state.tab === "bin"){
      $("previewIcon").textContent="📦";
      $("previewTitle").textContent="Box";
      $("previewCode").textContent=`${num("bin_x")}×${num("bin_y")}×${num("bin_z")}`;
      $("kpiType").textContent="Box";
    } else {
      $("previewIcon").textContent="🟦";
      $("previewTitle").textContent="Baseplate";
      $("previewCode").textContent=`${num("bp_x")}×${num("bp_y")}`;
      $("kpiType").textContent="Baseplate";
    }

    $("kpiTool").textContent = tool.name;
    $("paramSummary").value = buildSummary();
    $("toolLink").value = link;

    // iframe attempt (may be blocked by tool)
    const frame = $("toolFrame");
    frame.src = "";
    if(tool.iframeLikely){
      frame.src = link;
    } else {
      // show empty frame; user uses Open button
      frame.src = "about:blank";
    }
  }

  function openSelectedTool(){
    const link = buildLink();
    window.open(link, "_blank", "noopener,noreferrer");
    toast("Generator geöffnet");
  }

  function copySummary(){
    const s = $("paramSummary");
    s.select();
    s.setSelectionRange(0, 99999);
    try{ document.execCommand("copy"); }catch(e){}
    toast("Summary kopiert");
  }

  // History (localStorage)
  function loadHistory(){
    try{
      return JSON.parse(localStorage.getItem("gf_history") || "[]");
    }catch(e){ return []; }
  }
  function saveHistory(){
    localStorage.setItem("gf_history", JSON.stringify(state.history));
    $("histCount").textContent = String(state.history.length);
  }

  function addHistory(){
    const entry = {
      ts: new Date().toISOString(),
      tab: state.tab,
      tool: currentTool().key,
      summary: buildSummary(),
      link: buildLink(),
      params: getParams()
    };
    state.history.unshift(entry);
    state.history = state.history.slice(0, 50);
    saveHistory();
    toast("In Verlauf gespeichert");
  }

  function getParams(){
    if(state.tab==="bin"){
      return {
        x:num("bin_x"), y:num("bin_y"), z:num("bin_z"),
        divx:num("bin_divx"), divy:num("bin_divy")
      };
    }
    return {
      x:num("bp_x"), y:num("bp_y"),
      style_plate: val("bp_style"),
      enable_magnet: val("bp_magnet")
    };
  }

  function renderHistory(){
    const wrap = $("historyList");
    wrap.innerHTML = "";
    if(state.history.length===0){
      wrap.innerHTML = `<div class="sidecard"><h3>Leer</h3><p>Noch keine Einträge gespeichert.</p></div>`;
      return;
    }
    state.history.forEach((h, idx)=>{
      const div = document.createElement("div");
      div.className = "hitem";
      div.innerHTML = `
        <div>
          <b>${escapeHtml(h.summary)}</b>
          <small>${escapeHtml(new Date(h.ts).toLocaleString("de-DE"))}</small>
        </div>
        <div class="right">
          <button class="btn" data-i="${idx}">Load</button>
          <button class="btn primary" data-o="${idx}">Open</button>
        </div>
      `;
      wrap.appendChild(div);

      div.querySelector(`[data-i="${idx}"]`).onclick = () => loadHistoryItem(idx);
      div.querySelector(`[data-o="${idx}"]`).onclick = () => window.open(h.link, "_blank", "noopener,noreferrer");
    });
  }

  function loadHistoryItem(idx){
    const h = state.history[idx];
    if(!h) return;

    $("toolSelect").value = h.tool || "perplexing";

    if(h.tab==="bin"){
      switchTab("bin");
      $("bin_x").value = h.params?.x ?? 2;
      $("bin_y").value = h.params?.y ?? 2;
      $("bin_z").value = h.params?.z ?? 6;
      $("bin_divx").value = h.params?.divx ?? 1;
      $("bin_divy").value = h.params?.divy ?? 1;
    } else {
      switchTab("baseplate");
      $("bp_x").value = h.params?.x ?? 4;
      $("bp_y").value = h.params?.y ?? 6;
      $("bp_style").value = h.params?.style_plate ?? "0";
      $("bp_magnet").value = h.params?.enable_magnet ?? "0";
    }
    updatePreview();
    toast("Geladen");
  }

  function clearHistory(){
    state.history = [];
    saveHistory();
    renderHistory();
    toast("Verlauf geleert");
  }

  function exportHistory(){
    const blob = new Blob([JSON.stringify(state.history, null, 2)], {type:"application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "gridfinity-ui-history.json";
    a.click();
    URL.revokeObjectURL(a.href);
    toast("Export erstellt");
  }

  function escapeHtml(s){
    return String(s)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll("\"","&quot;")
      .replaceAll("'","&#039;");
  }

  function init(){
    $("histCount").textContent = String(state.history.length);
    updatePreview();
  }

  return {
    init, setView, switchTab, defaults,
    openSelectedTool, copySummary,
    addHistory, clearHistory, exportHistory, updatePreview
  };
})();

window.UI = UI;
window.addEventListener("DOMContentLoaded", UI.init);
