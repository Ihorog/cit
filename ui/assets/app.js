(() => {
  window.CIT_API = 'http://127.0.0.1:8790';

  const $ = (id) => document.getElementById(id);

  async function httpJSON(url, opt={}){
    const r = await fetch(url, opt);
    const t = await r.text();
    let j=null; try{ j=JSON.parse(t);}catch{}
    return { ok:r.ok, status:r.status, text:t, json:j };
  }

  function nodeCard(n){
    const a = document.createElement('a');
    a.className = 'card';
    a.href = n._page || '#';

    const h3 = document.createElement('h3');
    h3.textContent = n.title || n.id;

    const sub = document.createElement('div');
    sub.className = 'sub';
    sub.textContent = (n._sub || '').trim();

    const tags = document.createElement('div');
    tags.className = 'tags';
    (n._tags || []).forEach(t => {
      const s = document.createElement('span');
      s.className = 'tag';
      s.textContent = t;
      tags.appendChild(s);
    });

    a.appendChild(h3);
    if (sub.textContent) a.appendChild(sub);
    a.appendChild(tags);

    return a;
  }

  async function render(){
    const api = window.CIT_API;
    const health = await httpJSON(`${api}/health`);
    $('healthPill').textContent = health.ok
      ? `здоров'я: ${health.json?.model || 'ok'} ${health.json?.ts || ''}`
      : `здоров'я: DOWN`;

    const reg = await httpJSON(`${api}/registry`);
    if (!reg.ok || !reg.json){
      $('nodesGrid').innerHTML = '';
      const d = document.createElement('div');
      d.className='mono';
      d.textContent = `Registry load failed (HTTP ${reg.status})\n` + (reg.text || '').slice(0, 600);
      $('nodesGrid').appendChild(d);
      return;
    }

    const nodes = reg.json.nodes || [];
    const cards = [];

    const canonMap = {
      "ci":        { page:"/pages/ci.html",        sub:"Центр / оператор", tags:["центр","контакт"] },
      "kazkar":    { page:"/pages/kazkar.html",    sub:"Пам'ять / легенда", tags:["земля","було"] },
      "podija":    { page:"/pages/podija.html",    sub:"Події / ініціації", tags:["вогонь","буде"] },
      "nastrij":   { page:"/pages/nastrij.html",   sub:"Стан / емоції",     tags:["вода","зараз"] },
      "malya":     { page:"/pages/malya.html",     sub:"Ідеї / інновації",  tags:["повітря","є"] },
      "calendar":  { page:"/pages/calendar.html",  sub:"Ритми / вузли",     tags:["час","цикли"] },
      "gallery":   { page:"/pages/gallery.html",   sub:"Архів / образи",    tags:["медіа","історії"] },
    };

    nodes.forEach(n => {
      const m = canonMap[n.id] || { page:"#", sub:"", tags:[] };
      cards.push({
        id: n.id,
        title: n.title || n.id,
        _page: m.page,
        _sub: m.sub,
        _tags: m.tags
      });

      // legend_ci subnode (if exists)
      if (n.id === 'kazkar' && Array.isArray(n.subnodes)){
        const hasLegend = n.subnodes.find(s => s.id === 'legend_ci' || s.node_id === 'legend_ci');
        if (hasLegend){
          cards.push({
            id: 'legend_ci',
            title: '✨Легенда Ci',
            _page: '/pages/legend_ci.html',
            _sub: 'Ядро бібліотеки',
            _tags: ['земля','було','ядро']
          });
        }
      }
    });

    $('nodesGrid').innerHTML = '';
    cards.forEach(c => $('nodesGrid').appendChild(nodeCard(c)));
  }

  window.CI_RENDER_DASHBOARD = render;
})();
