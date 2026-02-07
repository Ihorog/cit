// Казкар — JavaScript для форми оповіді

const API_BASE = '/api/kazkar';

// Стан додатку
let kazkarState = {
    aktyvna: false,
    tsilisnist: 0
};

// Ініціалізація при завантаженні
document.addEventListener('DOMContentLoaded', () => {
    initializeKazkar();
});

async function initializeKazkar() {
    // Прив'язка обробників подій
    document.getElementById('btn-activate')?.addEventListener('click', aktyvuvatyKazkar);
    document.getElementById('btn-enter-legenda')?.addEventListener('click', uviytyVLegendu);
    document.getElementById('btn-plesty')?.addEventListener('click', plestyZvyaznist);
    
    // Завантажити початковий стан
    await onovytyProyav();
}

async function aktyvuvatyKazkar() {
    const btn = document.getElementById('btn-activate');
    const status = document.getElementById('activation-status');
    
    btn.disabled = true;
    status.textContent = 'Активація...';
    
    try {
        const response = await fetch(`${API_BASE}/aktyvuvaty`);
        const data = await response.json();
        
        kazkarState.aktyvna = true;
        kazkarState.tsilisnist = data.tsilisnist || 0.8;
        
        status.textContent = '✨ Казкар активовано!';
        onovytyTsilisnist(kazkarState.tsilisnist);
        
        // Показати секції
        document.getElementById('legenda-card').style.display = 'block';
        document.getElementById('zv-yaznist-section').style.display = 'block';
        document.getElementById('opovidi-section').style.display = 'block';
        document.getElementById('arkhetypy-section').style.display = 'block';
        
        // Приховати кнопку активації
        setTimeout(() => {
            document.getElementById('activation-section').style.display = 'none';
        }, 2000);
        
        // Завантажити архетипи та оповіді
        await zavantazhytyArkhetypy();
        await zavantazhytyOpovidi();
        
    } catch (error) {
        console.error('Помилка активації:', error);
        status.textContent = '❌ Помилка активації';
        btn.disabled = false;
    }
}

function uviytyVLegendu() {
    window.location.href = 'legenda.html';
}

async function plestyZvyaznist() {
    const textarea = document.getElementById('podiyi-input');
    const resultDiv = document.getElementById('opovid-result');
    const btn = document.getElementById('btn-plesty');
    
    const text = textarea.value.trim();
    if (!text) {
        resultDiv.innerHTML = '<p style="color: #ff6b6b;">Введіть події!</p>';
        return;
    }
    
    const podiyi = text.split('\n').filter(p => p.trim());
    
    btn.disabled = true;
    resultDiv.innerHTML = '<p>Плетіння зв\'язності...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/plesty-zv-yaznist`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ podiyi })
        });
        
        const data = await response.json();
        
        if (data.opovid) {
            const arkhetypInfo = data.opovid.arkhetyp 
                ? `<div><strong>Архетип:</strong> ${data.opovid.arkhetyp.symvol} ${data.opovid.arkhetyp.nazva}</div>`
                : '';
            
            resultDiv.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <strong>Оповідь #${data.opovid.id}</strong>
                </div>
                ${arkhetypInfo}
                <div style="margin-top: 1rem;">
                    <strong>Події:</strong>
                    <ul style="margin-top: 0.5rem;">
                        ${podiyi.map(p => `<li>${p}</li>`).join('')}
                    </ul>
                </div>
                <div style="margin-top: 1rem; color: var(--color-text-dim);">
                    Цілісність: ${(data.tsilisnist * 100).toFixed(0)}%
                </div>
            `;
            
            onovytyTsilisnist(data.tsilisnist);
            
            // Оновити список оповідей
            await zavantazhytyOpovidi();
        }
        
    } catch (error) {
        console.error('Помилка плетіння:', error);
        resultDiv.innerHTML = '<p style="color: #ff6b6b;">❌ Помилка створення оповіді</p>';
    } finally {
        btn.disabled = false;
    }
}

async function zavantazhytyArkhetypy() {
    try {
        const response = await fetch(`${API_BASE}/arkhetypy`);
        const data = await response.json();
        
        const grid = document.getElementById('arkhetypy-grid');
        if (!grid || !data.arkhetypy) return;
        
        grid.innerHTML = data.arkhetypy.map(arkh => `
            <div class="arkhetyp-card">
                <div class="arkhetyp-symvol">${arkh.symvol}</div>
                <div class="arkhetyp-nazva">${arkh.nazva}</div>
                <div class="arkhetyp-sutnist">${arkh.sutnist}</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Помилка завантаження архетипів:', error);
    }
}

async function zavantazhytyOpovidi() {
    try {
        const response = await fetch(`${API_BASE}/opovidi/ostanni?kilkist=5`);
        const data = await response.json();
        
        const list = document.getElementById('opovidi-list');
        if (!list || !data.opovidi || data.opovidi.length === 0) {
            if (list) list.innerHTML = '<p style="text-align: center; color: var(--color-text-dim);">Поки немає оповідей</p>';
            return;
        }
        
        list.innerHTML = data.opovidi.map(opovid => {
            const arkhetypInfo = opovid.arkhetyp 
                ? `${opovid.arkhetyp.symvol} ${opovid.arkhetyp.nazva}`
                : '—';
            
            return `
                <div class="opovid-item">
                    <div class="opovid-item-meta">
                        Оповідь #${opovid.id} | Архетип: ${arkhetypInfo}
                    </div>
                    <div>${opovid.kilkist_podiy} подій</div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Помилка завантаження оповідей:', error);
    }
}

async function onovytuProyav() {
    try {
        const response = await fetch(`${API_BASE}/proyav`);
        const data = await response.json();
        
        if (data.aktyvna) {
            kazkarState.aktyvna = true;
            kazkarState.tsilisnist = data.tsilisnist || 0;
            onovytyTsilisnist(kazkarState.tsilisnist);
        }
        
    } catch (error) {
        console.error('Помилка отримання прояву:', error);
    }
}

function onovytyTsilisnist(riven) {
    const fill = document.getElementById('tsilisnist-fill');
    const value = document.getElementById('tsilisnist-value');
    
    if (fill) {
        fill.style.width = `${riven * 100}%`;
    }
    
    if (value) {
        value.textContent = `${(riven * 100).toFixed(0)}%`;
    }
}
