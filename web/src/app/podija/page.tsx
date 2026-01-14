'use client';

import { useState, useEffect } from 'react';

export default function PodijaPage() {
  const [health, setHealth] = useState<string>('...');
  const [events, setEvents] = useState<any[]>([]);
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

  const loadEvents = async () => {
    try {
      const res = await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.event.list',
          input: { node_id: 'podija' }
        })
      });
      const data = await res.json();
      if (data.result?.events) {
        setEvents(data.result.events);
      }
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadEvents();
  }, []);

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">ПоДія</div>
          <div className="pills">
            <span className="pill">події / ініціації</span>
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
            <h2>ПоДія — Події та Ініціації</h2>
          </div>
          <div className="body">
            <div className="mono">
              ПоДія — події, запуск, ініціації (буде).
              {'\n\n'}
              Модуль планування подій та календаря.
              {'\n'}
              Тут буде інтерфейс для створення та управління подіями.
            </div>

            {events.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>Події:</h3>
                <div className="grid" style={{ gridTemplateColumns: '1fr', gap: '8px' }}>
                  {events.map((event, idx) => (
                    <div key={idx} className="card" style={{ gridColumn: 'span 1' }}>
                      <div style={{ fontSize: '13px', color: 'var(--muted)' }}>
                        {JSON.stringify(event, null, 2)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head">
            <h2>Створити подію</h2>
          </div>
          <div className="body">
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const eventData = {
                title: formData.get('title'),
                description: formData.get('description'),
                date: formData.get('date'),
                time: formData.get('time')
              };
              console.log('Create event:', eventData);
              // TODO: Implement event creation
            }}>
              <div style={{ display: 'grid', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                    Назва події
                  </label>
                  <input type="text" name="title" placeholder="Введіть назву події" required />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                    Опис
                  </label>
                  <textarea name="description" placeholder="Опис події" rows={3} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Дата
                    </label>
                    <input type="date" name="date" required />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Час
                    </label>
                    <input type="time" name="time" required />
                  </div>
                </div>
                <button type="submit" className="btn" style={{ marginTop: '8px' }}>
                  Створити подію
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @import url('/ci.css');
      `}</style>
    </>
  );
}
