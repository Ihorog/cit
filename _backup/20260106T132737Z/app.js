(() => {
  const qs = (s, el=document) => el.querySelector(s);
  const qsa = (s, el=document) => [...el.querySelectorAll(s)];
  const esc = (s="") => (""+s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));

  const params = new URLSearchParams(location.search);
  const API = params.get("api") || localStorage.getItem("cit_api") || "http://127.0.0.1:8790";
  localStorage.setItem("cit_api", API);

  function toast(msg){
    const t = qs("#toast");
    if(!t) return alert(msg);
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(()=>t.classList.remove("show"), 1800);
  }

  async function apiGet(path){
    const r = await fetch(API + path, {method:"GET"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }
  async function apiText(path){
    const r = await fetch(API + path, {method:"GET"});
    if(!r.ok) throw new Error(await r.text());
    return await r.text();
  }
  async function apiPost(path, body, headers){
    const r = await fetch(API + path, {method:"POST", body, headers});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }
  async function apiDelete(path){
    const r = await fetch(API + path, {method:"DELETE"});
    if(!r.ok) throw new Error(await r.text());
    return await r.json();
  }

  function openModal(id){ qs(id).classList.add("open"); }
  function closeModal(id){ qs(id).classList.remove("open"); }

  async function refreshFiles(){
    const box = qs("#filesList");
    const st  = qs("#filesStatus");
    if(!box) return;
    st.textContent = "loading…";
    try{
      const data = await apiGet("/files");
      const items = data.items || [];
      st.textContent = items.length ? `${items.length} файл(и)` : "порожньо";
      box.innerHTML = items.map(it => {
        const name = esc(it.name);
        const size = esc(it.size);
        const mtime = esc(it.mtime || "");
        return `
          <div class="fileRow">
            <div class="fileMeta">
              <div class="fileName">${name}</div>
              <div class="fileSub">${size} байт • ${mtime}</div>
            </div>
            <div class="fileActions">
              <button class="btn mini" data-dl="${encodeURIComponent(it.name)}">Відкрити</button>
              <button class="btn mini danger" data-del="${encodeURIComponent(it.name)}">Видалити</button>
            </div>
          </div>`;
      }).join("");
    }catch(e){
      st.textContent = "ERR";
      box.innerHTML = `<div class="mono small">Помилка: ${esc(e.message||String(e))}</div>`;
    }
  }

  async function uploadFile(file, kind){
    const fd = new FormData();
    fd.append("file", file, file.name);
    fd.append("kind", kind || "file");
    return await apiPost("/upload", fd);
  }

  async function ensureUI(){
    // tech buttons
    const bar = qs("#chatBar");
    if(!bar) return;

    const left = qs("#chatLeft");
    const right = qs("#chatRight");

    // attach inputs
    const fileInput = qs("#fileInput");
    const imgInput  = qs("#imgInput");

    qsa("[data-open-modal]").forEach(b=>{
      b.addEventListener("click", ()=>openModal(b.getAttribute("data-open-modal")));
    });
    qsa("[data-close-modal]").forEach(b=>{
      b.addEventListener("click", ()=>closeModal(b.getAttribute("data-close-modal")));
    });

    qs("#btnAttachFile").addEventListener("click", ()=>fileInput.click());
    qs("#btnAttachImg").addEventListener("click", ()=>imgInput.click());
    qs("#btnFiles").addEventListener("click", async ()=>{ openModal("#modalFiles"); await refreshFiles(); });

    fileInput.addEventListener("change", async (e)=>{
      const f = e.target.files && e.target.files[0];
      if(!f) return;
      toast("Завантаження…");
      try{
        const res = await uploadFile(f, "file");
        toast("Збережено");
        await refreshFiles();
        // inject message into chat input
        const input = qs("#userInput");
        input.value = (input.value||"") + `\n[файл збережено] name=${res.name} path=${res.path}`;
        input.focus();
      }catch(err){
        toast("ERR upload");
        alert(err.message||String(err));
      }finally{
        e.target.value = "";
      }
    });

    imgInput.addEventListener("change", async (e)=>{
      const f = e.target.files && e.target.files[0];
      if(!f) return;
      toast("Завантаження…");
      try{
        const res = await uploadFile(f, "image");
        toast("Зображення збережено");
        await refreshFiles();
        const input = qs("#userInput");
        input.value = (input.value||"") + `\n[зображення збережено] name=${res.name} path=${res.path}`;
        input.focus();
      }catch(err){
        toast("ERR upload");
        alert(err.message||String(err));
      }finally{
        e.target.value = "";
      }
    });

    // files actions
    qs("#filesList").addEventListener("click", async (e)=>{
      const dl = e.target && e.target.getAttribute && e.target.getAttribute("data-dl");
      const del = e.target && e.target.getAttribute && e.target.getAttribute("data-del");
      if(dl){
        const url = API + "/file?name=" + dl;
        window.open(url, "_blank");
        return;
      }
      if(del){
        if(!confirm("Видалити файл?")) return;
        toast("Видалення…");
        try{
          await apiDelete("/file?name=" + del);
          toast("Видалено");
          await refreshFiles();
        }catch(err){
          toast("ERR delete");
          alert(err.message||String(err));
        }
      }
    });

    // config load/save
    async function loadCfg(){
      try{
        const cfg = await apiGet("/config");
        qs("#cfg_openai").value = (cfg.openai_api_key_masked || "");
        qs("#cfg_model").value = (cfg.model || "");
        qs("#cfg_storage").value = (cfg.storage_mode || "");
        qs("#cfg_vault").value = (cfg.vault_dir || "");
        qs("#cfg_webdav_url").value = (cfg.webdav_url || "");
        qs("#cfg_webdav_user").value = (cfg.webdav_user || "");
        // never show pass
        qs("#cfg_webdav_pass").value = "";
      }catch(e){
        // ignore
      }
    }

    qs("#btnSettings").addEventListener("click", async ()=>{
      openModal("#modalSettings");
      await loadCfg();
    });

    qs("#btnSaveCfg").addEventListener("click", async ()=>{
      const payload = {
        openai_api_key: qs("#cfg_openai_new").value.trim(),
        model: qs("#cfg_model").value.trim(),
        storage_mode: qs("#cfg_storage").value.trim(),
        vault_dir: qs("#cfg_vault").value.trim(),
        webdav_url: qs("#cfg_webdav_url").value.trim(),
        webdav_user: qs("#cfg_webdav_user").value.trim(),
        webdav_pass: qs("#cfg_webdav_pass").value.trim(),
      };
      toast("Збереження…");
      try{
        await apiPost("/config", JSON.stringify(payload), {"Content-Type":"application/json"});
        toast("Збережено");
        qs("#cfg_openai_new").value = "";
        qs("#cfg_webdav_pass").value = "";
        await loadCfg();
      }catch(err){
        toast("ERR config");
        alert(err.message||String(err));
      }
    });

    // self-check
    qs("#btnSelfCheck").addEventListener("click", async ()=>{
      toast("Self-check…");
      try{
        const h = await apiGet("/health");
        const c = await apiGet("/config");
        toast("OK");
        qs("#selfcheckOut").textContent =
          `health.ok=${h.ok}\nmodel=${h.model}\nstorage=${c.storage_mode}\nvault=${c.vault_dir}\nwebdav=${c.webdav_url||""}`;
      }catch(err){
        toast("ERR");
        qs("#selfcheckOut").textContent = "ERR: " + (err.message||String(err));
      }
    });

    // show api label
    const ap = qs("#apiLabel");
    if(ap) ap.textContent = API;
  }

  document.addEventListener("DOMContentLoaded", ensureUI);
})();
