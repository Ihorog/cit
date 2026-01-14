'use client';

import { useState, useEffect } from 'react';

export default function MalyaPage() {
  const [health, setHealth] = useState<string>('...');
  const [ideas, setIdeas] = useState<any[]>([]);
  const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8790';

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API}/health`);
      const data = await res.json();
      setHealth(`${data.model || 'ok'} ${data.ts || ''}`);
    } catch {
      setHealth('DOWN');
    }
  };

  const loadIdeas = async () => {
    try {
      const res = await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.get',
          input: { node_id: 'malya', key: 'ideas' }
        })
      });
      const data = await res.json();
      if (data.result?.value) {
        setIdeas(JSON.parse(data.result.value) || []);
      }
    } catch (err) {
      console.error('Failed to load ideas:', err);
    }
  };

  const saveIdea = async (title: string, description: string, category: string) => {
    try {
      const idea = {
        id: Date.now().toString(),
        title,
        description,
        category,
        timestamp: new Date().toISOString(),
        status: 'нова'
      };
      const newIdeas = [...ideas, idea];
      
      await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.set',
          input: { 
            node_id: 'malya', 
            key: 'ideas',
            value: JSON.stringify(newIdeas)
          }
        })
      });
      
      setIdeas(newIdeas);
    } catch (err) {
      console.error('Failed to save idea:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadIdeas();
  }, []);

  const categories = [
    { value: 'творчість', label: '🎨 Творчість', color: '#FF6B9D' },
    { value: 'технології', label: '💻 Технології', color: '#4ECDC4' },
    { value: 'навчання', label: '📚 Навчання', color: '#FFE66D' },
    { value: 'бізнес', label: '💼 Бізнес', color: '#95E1D3' },
    { value: 'інше', label: '✨ Інше', color: '#C7CEEA' }
  ];

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">Маля</div>
          <div className="pills">
            <span className="pill">ідеї / інновації</span>
            <span className="pill">API: {API.replace('http://', '')}</span>
            <span className="pill">здоров'я: {health}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <a className="btn ghost" href="/">Дашборд</a>
          <button className="btn" onClick={checkHealth}>Оновити</button>
        </div>
      </div>

      <div className="wrap">
        <div className="section">
          <div className="head">
            <h2>Маля — Ідеї та Інновації</h2>
          </div>
          <div className="body">
            <div className="mono">
              Маля — ідеї, альтернативи (є).
              {'\n\n'}
              Творчий модуль для збереження та розвитку ідей.
              {'\n'}
              Тут можна записувати свої думки, проєкти та інновації.
            </div>
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head">
            <h2>Нова ідея</h2>
          </div>
          <div className="body">
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const title = formData.get('title') as string;
              const description = formData.get('description') as string;
              const category = formData.get('category') as string;
              saveIdea(title, description, category);
              e.currentTarget.reset();
            }}>
              <div style={{ display: 'grid', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                    Назва ідеї
                  </label>
                  <input type="text" name="title" placeholder="Коротка назва ідеї" required />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                    Опис
                  </label>
                  <textarea name="description" placeholder="Детальний опис ідеї" rows={4} required />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                    Категорія
                  </label>
                  <select name="category" required>
                    {categories.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
                <button type="submit" className="btn" style={{ marginTop: '8px' }}>
                  Зберегти ідею
                </button>
              </div>
            </form>
          </div>
        </div>

        {ideas.length > 0 && (
          <div className="section" style={{ marginTop: '16px' }}>
            <div className="head">
              <h2>Мої ідеї ({ideas.length})</h2>
            </div>
            <div className="body">
              <div className="grid">
                {ideas.slice().reverse().map((idea) => {
                  const cat = categories.find(c => c.value === idea.category);
                  return (
                    <div key={idea.id} className="card">
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <h3 style={{ margin: 0, fontSize: '16px' }}>{idea.title}</h3>
                        <span className="tag" style={{ 
                          background: cat?.color || '#C7CEEA',
                          color: '#000',
                          border: 'none',
                          fontWeight: 'bold'
                        }}>
                          {cat?.label || idea.category}
                        </span>
                      </div>
                      <div className="sub" style={{ marginBottom: '10px' }}>
                        {idea.description}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--muted)' }}>
                        {new Date(idea.timestamp).toLocaleDateString('uk-UA')}
                      </div>
                      <div className="tags" style={{ marginTop: '8px' }}>
                        <span className="tag">{idea.status}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        @import url('/ci.css');
      `}</style>
    </>
  );
}
