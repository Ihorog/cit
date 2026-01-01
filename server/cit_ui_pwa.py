UI_HTML_PWA = """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<meta name="theme-color" content="#4fc3f7">
<title>CIMEIKA</title>
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icons/icon-192.png">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0b0f14;--bg2:#141920;--txt:#e0e0e0;--txt2:#9e9e9e;--acc:#4fc3f7;--bor:#2a2e35}
body{font-family:sans-serif;background:var(--bg);color:var(--txt);height:100vh;overflow:hidden;display:flex;flex-direction:column}
#header{background:var(--bg2);border-bottom:1px solid var(--bor);padding:12px 16px;display:flex;align-items:center;gap:12px}
#menuBtn{background:none;border:none;color:var(--acc);font-size:24px;cursor:pointer;padding:8px}
#logo{font-size:20px;font-weight:700;color:var(--acc);flex:1}
#sidebar{position:fixed;top:0;left:-280px;width:280px;height:100vh;background:var(--bg2);border-right:1px solid var(--bor);transition:left .3s;z-index:1000;overflow-y:auto}
#sidebar.active{left:0}
#overlay{position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,.5);opacity:0;pointer-events:none;transition:opacity .3s;z-index:999}
#overlay.active{opacity:1;pointer-events:all}
.section{padding:16px;border-bottom:1px solid var(--bor)}
.title{font-size:12px;font-weight:600;color:var(--txt2);text-transform:uppercase;margin-bottom:12px}
.item{padding:10px 12px;margin:4px 0;border-radius:6px;cursor:pointer}
.item:hover{background:var(--bg)}
#chatLog{flex:1;overflow-y:auto;padding:16px}
.message{margin-bottom:16px}
.message.user{text-align:right}
.message-content{display:inline-block;max-width:80%;padding:12px 16px;border-radius:12px;word-wrap:break-word}
.message.user .message-content{background:var(--acc);color:var(--bg)}
.message.assistant .message-content{background:var(--bg2);border:1px solid var(--bor)}
#inputArea{background:var(--bg2);border-top:1px solid var(--bor);padding:12px 16px}
#inputForm{display:flex;gap:8px}
#userInput{flex:1;background:var(--bg);border:1px solid var(--bor);border-radius:8px;padding:12px 16px;color:var(--txt);font-size:15px}
#sendBtn{background:var(--acc);color:var(--bg);border:none;border-radius:8px;padding:12px 20px;font-weight:600}
</style>
</head>
<body>
<div id="header">
<button id="menuBtn">☰</button>
<div id="logo">CIMEIKA</div>
</div>
<div id="overlay"></div>
<div id="sidebar">
<div class="section">
<div class="title">Історія</div>
<div id="chatHistory"></div>
</div>
<div class="section">
<div class="title">Модулі</div>
<div class="item" data-module="kazkar">📖 Казкар</div>
<div class="item" data-module="event">🎯 Подія</div>
<div class="item" data-module="mood">🎭 Настрій</div>
<div class="item" data-module="idea">💡 Маля</div>
<div class="item" data-module="calendar">📅 Календар</div>
<div class="item" data-module="gallery">🖼️ Галерея</div>
</div>
<div class="section">
<div class="title">Ресурси</div>
<div class="item" onclick="window.open('https://github.com/ihorog/cit','_blank')">🔗 GitHub</div>
<div class="item" onclick="window.open('https://ihorog-cimeika-api.hf.space','_blank')">🤗 HF</div>
</div>
<div class="section">
<div class="item" id="clearBtn">🗑️ Очистити</div>
</div>
</div>
<div id="chatLog"></div>
<div id="inputArea">
<form id="inputForm">
<input type="text" id="userInput" placeholder="Напиши...">
<button type="submit" id="sendBtn">→</button>
</form>
</div>
<script>
let cid=null,msgs=[];
const menu=document.getElementById('menuBtn'),
sb=document.getElementById('sidebar'),
ov=document.getElementById('overlay'),
log=document.getElementById('chatLog'),
form=document.getElementById('inputForm'),
inp=document.getElementById('userInput'),
btn=document.getElementById('sendBtn'),
hist=document.getElementById('chatHistory'),
clr=document.getElementById('clearBtn');

menu.onclick=()=>{sb.classList.add('active');ov.classList.add('active')};
ov.onclick=()=>{sb.classList.remove('active');ov.classList.remove('active')};

function loadHist(){
const c=JSON.parse(localStorage.getItem('cimeika_chats')||'{}'),
ids=Object.keys(c).sort((a,b)=>c[b].timestamp-c[a].timestamp);
hist.innerHTML='';
ids.forEach(id=>{
const ch=c[id],it=document.createElement('div');
it.className='item';
it.textContent=ch.title||'Новий';
it.onclick=()=>loadChat(id);
hist.appendChild(it);
});
}

function saveChat(){
if(!cid)cid='chat_'+Date.now();
const c=JSON.parse(localStorage.getItem('cimeika_chats')||'{}');
c[cid]={id:cid,title:msgs[0]?.content?.substring(0,30)||'Новий',messages:msgs,timestamp:Date.now()};
localStorage.setItem('cimeika_chats',JSON.stringify(c));
loadHist();
}

function loadChat(id){
const c=JSON.parse(localStorage.getItem('cimeika_chats')||'{}');
if(c[id]){cid=id;msgs=c[id].messages;render();sb.classList.remove('active');ov.classList.remove('active')}
}

function render(){
log.innerHTML='';
msgs.forEach(m=>{
const d=document.createElement('div');
d.className='message '+m.role;
d.innerHTML='<div class="message-content">'+m.content+'</div>';
log.appendChild(d);
});
log.scrollTop=log.scrollHeight;
}

form.onsubmit=async e=>{
e.preventDefault();
const t=inp.value.trim();
if(!t)return;
msgs.push({role:'user',content:t});
render();
inp.value='';
btn.disabled=true;
try{
const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:msgs})});
const d=await r.json();
if(d.response){msgs.push({role:'assistant',content:d.response});render();saveChat()}
}catch(err){msgs.push({role:'assistant',content:'Помилка'});render()}
btn.disabled=false;
};

clr.onclick=()=>{if(confirm('Видалити історію?')){localStorage.removeItem('cimeika_chats');loadHist();cid=null;msgs=[];log.innerHTML=''}};

document.querySelectorAll('[data-module]').forEach(el=>{
el.onclick=()=>{alert('Модуль в розробці');sb.classList.remove('active');ov.classList.remove('active')}
});

loadHist();
</script>
</body>
</html>
"""
