// Легенда Сі — JavaScript для навігації по семантичному графу

const API_BASE = '/api/kazkar';

// Стан легенди
let legendaState = {
    potochnyyVuzol: null,
    grafData: null,
    istoriya: []
};

// Ініціалізація
document.addEventListener('DOMContentLoaded', () => {
    initializeLegenda();
});

async function initializeLegenda() {
    // Прив'язка обробників
    document.getElementById('btn-search')?.addEventListener('click', vykonatyPoshuk);
    document.getElementById('search-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') vykonatyPoshuk();
    });
    
    // Обробники для форм редагування
    document.getElementById('form-create-node')?.addEventListener('submit', stvorytyVuzol);
    document.getElementById('form-add-link')?.addEventListener('submit', dodatyZvyazok);
    
    // Активувати легенду і завантажити початковий вузол
    await aktyvuvatyLegendu();
}

async function aktyvuvatyLegendu() {
    try {
        const response = await fetch(`${API_BASE}/legenda/aktyvuvaty`);
        const data = await response.json();
        
        if (data.aktyvatsiya && data.aktyvatsiya.potochnyy_vuzol) {
            await vidbrazytyVuzol(data.aktyvatsiya.potochnyy_vuzol);
        }
        
        // Завантажити повний граф
        await zavantazhytyGraf();
        
    } catch (error) {
        console.error('Помилка активації легенди:', error);
    }
}

async function navihuvaty(vuzolId) {
    try {
        const response = await fetch(`${API_BASE}/legenda/navihuvaty/${vuzolId}`);
        const data = await response.json();
        
        if (data.potochnyy_vuzol) {
            await vidbrazytyVuzol(data.potochnyy_vuzol);
            
            // Оновити історію
            if (data.istoriya) {
                legendaState.istoriya = data.istoriya;
                vidbrazytyIstoriyu();
            }
            
            // Оновити граф (виділити поточний вузол)
            if (legendaState.grafData) {
                malyuvatyGraf(vuzolId);
            }
        }
        
    } catch (error) {
        console.error('Помилка навігації:', error);
    }
}

function vidbrazytyVuzol(vuzol) {
    legendaState.potochnyyVuzol = vuzol;
    
    // Оновити картку вузла
    document.getElementById('node-depth').textContent = vuzol.hlybyna;
    document.getElementById('node-title').textContent = vuzol.nazva;
    document.getElementById('node-description').textContent = vuzol.opys;
    
    if (vuzol.arkhetyp) {
        document.getElementById('archetype-name').textContent = vuzol.arkhetyp;
    }
    
    // Відобразити резонуючі сенси
    const tagsDiv = document.getElementById('resonance-tags');
    if (tagsDiv && vuzol.rezonansni_sensy) {
        tagsDiv.innerHTML = vuzol.rezonansni_sensy
            .map(sens => `<div class="resonance-tag">${sens}</div>`)
            .join('');
    }
    
    // Відобразити доступні шляхи
    vidbrazytyShlyakhy();
}

async function vidbrazytyShlyakhy() {
    try {
        const vuzolId = legendaState.potochnyyVuzol?.id;
        if (!vuzolId) return;
        
        const response = await fetch(`${API_BASE}/legenda/navihuvaty/${vuzolId}`);
        const data = await response.json();
        
        const pathsGrid = document.getElementById('paths-grid');
        if (!pathsGrid || !data.zv_yazani_vuzly) return;
        
        pathsGrid.innerHTML = data.zv_yazani_vuzly
            .map(zv => `
                <div class="path-card" onclick="navihuvaty('${zv.id}')">
                    <div class="path-card-title">${zv.nazva}</div>
                    <div class="path-card-depth">Глибина: ${zv.hlybyna}</div>
                </div>
            `)
            .join('');
        
    } catch (error) {
        console.error('Помилка відображення шляхів:', error);
    }
}

function vidbrazytyIstoriyu() {
    const breadcrumbs = document.getElementById('history-breadcrumbs');
    if (!breadcrumbs || !legendaState.istoriya) return;
    
    breadcrumbs.innerHTML = legendaState.istoriya
        .map((vuzolId, index) => {
            const arrow = index < legendaState.istoriya.length - 1 
                ? '<span class="breadcrumb-arrow">→</span>' 
                : '';
            return `<div class="breadcrumb-item">${vuzolId}</div>${arrow}`;
        })
        .join('');
}

async function zavantazhytyGraf() {
    try {
        const response = await fetch(`${API_BASE}/legenda/eksport`);
        const data = await response.json();
        
        if (data.legenda && data.legenda.vuzly) {
            legendaState.grafData = data.legenda;
            malyuvatyGraf(legendaState.potochnyyVuzol?.id);
        }
        
    } catch (error) {
        console.error('Помилка завантаження графа:', error);
    }
}

function malyuvatyGraf(activeVuzolId = null) {
    const svg = document.getElementById('graph-svg');
    if (!svg || !legendaState.grafData) return;
    
    const vuzly = legendaState.grafData.vuzly;
    const width = svg.clientWidth || 800;
    const height = 400;
    
    // Очистити SVG
    svg.innerHTML = '';
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    
    // Розмістити вузли по колах (за глибиною)
    const positions = {};
    const centerX = width / 2;
    const centerY = height / 2;
    const radiusStep = 80;
    
    vuzly.forEach(vuzol => {
        const depth = vuzol.hlybyna;
        const radius = depth * radiusStep;
        
        // Підрахувати кількість вузлів на цій глибині
        const vuzlyNaHlybыni = vuzly.filter(v => v.hlybyna === depth);
        const index = vuzlyNaHlybыni.findIndex(v => v.id === vuzol.id);
        const angle = (index / vuzlyNaHlybыni.length) * 2 * Math.PI;
        
        positions[vuzol.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    });
    
    // Намалювати зв'язки
    vuzly.forEach(vuzol => {
        const pos1 = positions[vuzol.id];
        if (!pos1) return;
        
        vuzol.zv_yazani_vuzly.forEach(zv_id => {
            const pos2 = positions[zv_id];
            if (!pos2) return;
            
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', pos1.x);
            line.setAttribute('y1', pos1.y);
            line.setAttribute('x2', pos2.x);
            line.setAttribute('y2', pos2.y);
            line.setAttribute('class', 'link-line');
            svg.appendChild(line);
        });
    });
    
    // Намалювати вузли
    vuzly.forEach(vuzol => {
        const pos = positions[vuzol.id];
        if (!pos) return;
        
        // Коло вузла
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', pos.x);
        circle.setAttribute('cy', pos.y);
        circle.setAttribute('r', 20);
        circle.setAttribute('class', `node-circle ${vuzol.id === activeVuzolId ? 'active' : ''}`);
        circle.onclick = () => navihuvaty(vuzol.id);
        svg.appendChild(circle);
        
        // Текст вузла
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', pos.x);
        text.setAttribute('y', pos.y + 30);
        text.setAttribute('class', 'node-label');
        text.textContent = vuzol.nazva;
        svg.appendChild(text);
    });
}

async function vykonatyPoshuk() {
    const input = document.getElementById('search-input');
    const resultsDiv = document.getElementById('search-results');
    
    const zapyt = input.value.trim();
    if (!zapyt) return;
    
    resultsDiv.innerHTML = '<p>Пошук...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/legenda/poshuk`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zapyt })
        });
        
        const data = await response.json();
        
        if (!data.znahkheni_vuzly || data.znahkheni_vuzly.length === 0) {
            resultsDiv.innerHTML = '<p style="color: var(--color-text-dim);">Нічого не знайдено</p>';
            return;
        }
        
        resultsDiv.innerHTML = data.znahkheni_vuzly
            .map(vuzol => `
                <div class="search-result-item" onclick="navihuvaty('${vuzol.id}')">
                    <strong>${vuzol.nazva}</strong> (глибина: ${vuzol.hlybyna})<br>
                    <span style="color: var(--color-text-dim); font-size: 0.9rem;">${vuzol.opys}</span>
                </div>
            `)
            .join('');
        
    } catch (error) {
        console.error('Помилка пошуку:', error);
        resultsDiv.innerHTML = '<p style="color: #ff6b6b;">Помилка пошуку</p>';
    }
}

// === Функції редагування графа ===

async function stvorytyVuzol(event) {
    event.preventDefault();
    
    const vuzolId = document.getElementById('new-node-id').value.trim();
    const nazva = document.getElementById('new-node-nazva').value.trim();
    const opys = document.getElementById('new-node-opys').value.trim();
    const hlybyna = parseInt(document.getElementById('new-node-hlybyna').value);
    const zvyazkyStr = document.getElementById('new-node-zvyazky').value.trim();
    const sensyStr = document.getElementById('new-node-sensy').value.trim();
    const arkhetyp = document.getElementById('new-node-arkhetyp').value.trim();
    
    // Парсинг списків
    const zv_yazani_vuzly = zvyazkyStr ? zvyazkyStr.split(',').map(s => s.trim()).filter(s => s) : [];
    const rezonansni_sensy = sensyStr ? sensyStr.split(',').map(s => s.trim()).filter(s => s) : [];
    
    try {
        const response = await fetch(`${API_BASE}/legenda/vuzol`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vuzol_id: vuzolId,
                nazva: nazva,
                opys: opys,
                hlybyna: hlybyna,
                zv_yazani_vuzly: zv_yazani_vuzly,
                rezonansni_sensy: rezonansni_sensy,
                arkhetyp: arkhetyp || null
            })
        });
        
        const data = await response.json();
        
        if (data.uspishno) {
            alert(`✅ Вузол "${nazva}" успішно створено!`);
            
            // Очистити форму
            document.getElementById('form-create-node').reset();
            
            // Оновити граф
            await zavantazhytyGraf();
            
            // Перейти до нового вузла
            await navihuvaty(vuzolId);
        } else {
            alert(`❌ Помилка: ${data.pomylka}`);
        }
        
    } catch (error) {
        console.error('Помилка створення вузла:', error);
        alert('❌ Помилка створення вузла');
    }
}

async function dodatyZvyazok(event) {
    event.preventDefault();
    
    const vuzolId1 = document.getElementById('link-node-1').value.trim();
    const vuzolId2 = document.getElementById('link-node-2').value.trim();
    
    if (!vuzolId1 || !vuzolId2) {
        alert('❌ Будь ласка, введіть обидва ID вузлів');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/legenda/zv-yazok`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vuzol_id_1: vuzolId1,
                vuzol_id_2: vuzolId2
            })
        });
        
        const data = await response.json();
        
        if (data.uspishno) {
            alert(`✅ Зв'язок між "${vuzolId1}" та "${vuzolId2}" створено!`);
            
            // Очистити форму
            document.getElementById('form-add-link').reset();
            
            // Оновити граф
            await zavantazhytyGraf();
            
            // Оновити відображення поточного вузла якщо це один з двох зв'язаних
            if (legendaState.potochnyyVuzol?.id === vuzolId1 || legendaState.potochnyyVuzol?.id === vuzolId2) {
                await vidbrazytyShlyakhy();
            }
        } else {
            alert(`❌ Помилка: ${data.pomylka}`);
        }
        
    } catch (error) {
        console.error('Помилка створення зв\'язку:', error);
        alert('❌ Помилка створення зв\'язку');
    }
}
