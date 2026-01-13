'use client';

import { useState, useEffect } from 'react';

export default function NastrijPage() {
  const [health, setHealth] = useState<string>('...');
  const [mood, setMood] = useState<string>('');
  const [moodHistory, setMoodHistory] = useState<any[]>([]);
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

  const loadMoodHistory = async () => {
    try {
      const res = await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.get',
          input: { node_id: 'nastrij', key: 'mood_history' }
        })
      });
      const data = await res.json();
      if (data.result?.value) {
        setMoodHistory(JSON.parse(data.result.value) || []);
      }
    } catch (err) {
      console.error('Failed to load mood history:', err);
    }
  };

  const saveMood = async (moodValue: string, note: string) => {
    try {
      const entry = {
        mood: moodValue,
        note,
        timestamp: new Date().toISOString()
      };
      const newHistory = [...moodHistory, entry];
      
      await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.set',
          input: { 
            node_id: 'nastrij', 
            key: 'mood_history',
            value: JSON.stringify(newHistory)
          }
        })
      });
      
      setMoodHistory(newHistory);
      setMood('');
    } catch (err) {
      console.error('Failed to save mood:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadMoodHistory();
  }, []);

  const moodEmojis = [
    { value: 'дуже_погано', emoji: '😢', label: 'Дуже погано' },
    { value: 'погано', emoji: '😟', label: 'Погано' },
    { value: 'нормально', emoji: '😐', label: 'Нормально' },
    { value: 'добре', emoji: '🙂', label: 'Добре' },
    { value: 'відмінно', emoji: '😄', label: 'Відмінно' }
  ];

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">Настрій</div>
          <div className="pills">
            <span className="pill">стан / емоції</span>
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
            <h2>Настрій — Емоційний стан</h2>
          </div>
          <div className="body">
            <div className="mono">
              Настрій — емоційний стан (зараз).
              {'\n\n'}
              Модуль для відстеження та аналізу емоційного стану.
            </div>
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head">
            <h2>Як ти себе почуваєш?</h2>
          </div>
          <div className="body">
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'space-around', marginBottom: '16px' }}>
              {moodEmojis.map((m) => (
                <button
                  key={m.value}
                  onClick={() => setMood(m.value)}
                  className={`btn ${mood === m.value ? '' : 'ghost'}`}
                  style={{ 
                    fontSize: '32px', 
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  title={m.label}
                >
                  <span>{m.emoji}</span>
                  <span style={{ fontSize: '11px' }}>{m.label}</span>
                </button>
              ))}
            </div>

            {mood && (
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const note = formData.get('note') as string;
                saveMood(mood, note);
                e.currentTarget.reset();
              }}>
                <div style={{ display: 'grid', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Додай нотатку (необов'язково)
                    </label>
                    <textarea name="note" placeholder="Що відбувається?" rows={3} />
                  </div>
                  <button type="submit" className="btn">
                    Зберегти настрій
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {moodHistory.length > 0 && (
          <div className="section" style={{ marginTop: '16px' }}>
            <div className="head">
              <h2>Історія настрою</h2>
            </div>
            <div className="body">
              <div style={{ display: 'grid', gap: '8px' }}>
                {moodHistory.slice(-10).reverse().map((entry, idx) => {
                  const moodData = moodEmojis.find(m => m.value === entry.mood);
                  return (
                    <div key={idx} className="card" style={{ gridColumn: 'span 1', padding: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '24px' }}>{moodData?.emoji || '😐'}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '13px', fontWeight: 'bold' }}>
                            {moodData?.label || entry.mood}
                          </div>
                          {entry.note && (
                            <div style={{ fontSize: '12px', color: 'var(--muted)', marginTop: '4px' }}>
                              {entry.note}
                            </div>
                          )}
                          <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '4px' }}>
                            {new Date(entry.timestamp).toLocaleString('uk-UA')}
                          </div>
                        </div>
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
