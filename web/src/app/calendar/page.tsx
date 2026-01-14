'use client';

import { useState, useEffect } from 'react';

export default function CalendarPage() {
  const [health, setHealth] = useState<string>('...');
  const [currentDate, setCurrentDate] = useState(new Date());
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
          action: 'actions.state.get',
          input: { node_id: 'calendar', key: 'events' }
        })
      });
      const data = await res.json();
      if (data.result?.value) {
        setEvents(JSON.parse(data.result.value) || []);
      }
    } catch (err) {
      console.error('Failed to load events:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadEvents();
  }, []);

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentDate);
  const monthNames = [
    'Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень',
    'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'
  ];
  const dayNames = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const today = new Date();
  const isToday = (day: number) => {
    return day === today.getDate() && 
           currentDate.getMonth() === today.getMonth() && 
           currentDate.getFullYear() === today.getFullYear();
  };

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">Календар</div>
          <div className="pills">
            <span className="pill">ритми / вузли</span>
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
            <h2>Календар — Вузли часу</h2>
          </div>
          <div className="body">
            <div className="mono">
              Календар — вузли часу, ритми, цикли.
              {'\n\n'}
              Модуль для відстеження часових циклів та ритмів життя.
            </div>
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <button className="btn ghost" onClick={prevMonth}>←</button>
            <h2 style={{ margin: 0 }}>
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h2>
            <button className="btn ghost" onClick={nextMonth}>→</button>
          </div>
          <div className="body">
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(7, 1fr)', 
              gap: '8px',
              marginBottom: '8px'
            }}>
              {dayNames.map((day) => (
                <div 
                  key={day} 
                  style={{ 
                    textAlign: 'center', 
                    fontWeight: 'bold',
                    fontSize: '12px',
                    color: 'var(--muted)',
                    padding: '8px'
                  }}
                >
                  {day}
                </div>
              ))}
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(7, 1fr)', 
              gap: '8px'
            }}>
              {Array.from({ length: startingDayOfWeek }).map((_, idx) => (
                <div key={`empty-${idx}`} style={{ padding: '16px' }} />
              ))}
              
              {Array.from({ length: daysInMonth }).map((_, idx) => {
                const day = idx + 1;
                const isTodayDate = isToday(day);
                
                return (
                  <div
                    key={day}
                    style={{
                      border: '1px solid var(--stroke)',
                      borderRadius: '12px',
                      padding: '16px 8px',
                      textAlign: 'center',
                      background: isTodayDate 
                        ? 'rgba(31,164,255,.15)' 
                        : 'rgba(15,22,32,.5)',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      position: 'relative'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(31,164,255,.25)';
                      e.currentTarget.style.transform = 'scale(1.05)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = isTodayDate 
                        ? 'rgba(31,164,255,.15)' 
                        : 'rgba(15,22,32,.5)';
                      e.currentTarget.style.transform = 'scale(1)';
                    }}
                  >
                    <div style={{ 
                      fontSize: '18px', 
                      fontWeight: isTodayDate ? 'bold' : 'normal',
                      color: isTodayDate ? 'var(--blue)' : 'var(--text)'
                    }}>
                      {day}
                    </div>
                    {isTodayDate && (
                      <div style={{ 
                        fontSize: '10px', 
                        color: 'var(--blue)',
                        marginTop: '4px'
                      }}>
                        Сьогодні
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head">
            <h2>Ритми та цикли</h2>
          </div>
          <div className="body">
            <div className="grid">
              <div className="card">
                <h3>🌙 Місячний цикл</h3>
                <div className="sub">Фаза місяця та її вплив</div>
                <div style={{ fontSize: '48px', textAlign: 'center', margin: '16px 0' }}>
                  🌓
                </div>
                <div className="tags">
                  <span className="tag">Перша чверть</span>
                </div>
              </div>

              <div className="card">
                <h3>☀️ Сонячний ритм</h3>
                <div className="sub">Світловий день</div>
                <div style={{ fontSize: '14px', textAlign: 'center', margin: '16px 0' }}>
                  <div>Схід: 07:42</div>
                  <div>Захід: 16:18</div>
                </div>
                <div className="tags">
                  <span className="tag">8 год 36 хв</span>
                </div>
              </div>

              <div className="card">
                <h3>🔄 Біоритми</h3>
                <div className="sub">Фізичний, емоційний, інтелектуальний</div>
                <div style={{ margin: '16px 0' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Фізичний</div>
                    <div style={{ 
                      height: '8px', 
                      background: 'rgba(31,164,255,.3)', 
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{ 
                        width: '75%', 
                        height: '100%', 
                        background: 'var(--blue)' 
                      }} />
                    </div>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Емоційний</div>
                    <div style={{ 
                      height: '8px', 
                      background: 'rgba(255,195,77,.3)', 
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{ 
                        width: '60%', 
                        height: '100%', 
                        background: 'var(--gold)' 
                      }} />
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--muted)' }}>Інтелектуальний</div>
                    <div style={{ 
                      height: '8px', 
                      background: 'rgba(31,164,255,.3)', 
                      borderRadius: '4px',
                      overflow: 'hidden'
                    }}>
                      <div style={{ 
                        width: '85%', 
                        height: '100%', 
                        background: 'var(--blue)' 
                      }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @import url('/ci.css');
      `}</style>
    </>
  );
}
