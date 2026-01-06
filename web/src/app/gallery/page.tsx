'use client';

import { useState, useEffect } from 'react';

export default function GalleryPage() {
  const [health, setHealth] = useState<string>('...');
  const [media, setMedia] = useState<any[]>([]);
  const [selectedMedia, setSelectedMedia] = useState<any>(null);
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

  const loadMedia = async () => {
    try {
      const res = await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.get',
          input: { node_id: 'gallery', key: 'media' }
        })
      });
      const data = await res.json();
      if (data.result?.value) {
        setMedia(JSON.parse(data.result.value) || []);
      }
    } catch (err) {
      console.error('Failed to load media:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadMedia();
  }, []);

  const mediaTypes = [
    { type: 'image', icon: '🖼️', label: 'Зображення' },
    { type: 'video', icon: '🎥', label: 'Відео' },
    { type: 'audio', icon: '🎵', label: 'Аудіо' },
    { type: 'document', icon: '📄', label: 'Документ' }
  ];

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">Галерея</div>
          <div className="pills">
            <span className="pill">архів / образи</span>
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
            <h2>Галерея — Медіа архів</h2>
          </div>
          <div className="body">
            <div className="mono">
              Галерея — медіа, історії, слайди.
              {'\n\n'}
              Модуль для збереження та перегляду медіа-контенту.
              {'\n'}
              Зображення, відео, аудіо та документи.
            </div>
          </div>
        </div>

        <div className="section" style={{ marginTop: '16px' }}>
          <div className="head">
            <h2>Завантажити медіа</h2>
          </div>
          <div className="body">
            <div style={{ 
              border: '2px dashed var(--stroke)', 
              borderRadius: '16px', 
              padding: '40px',
              textAlign: 'center',
              background: 'rgba(11,15,20,.3)'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📁</div>
              <div style={{ fontSize: '14px', color: 'var(--muted)', marginBottom: '16px' }}>
                Перетягніть файли сюди або натисніть для вибору
              </div>
              <input 
                type="file" 
                multiple 
                accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                style={{ display: 'none' }}
                id="fileInput"
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  console.log('Selected files:', files);
                  // TODO: Implement file upload
                }}
              />
              <button 
                className="btn" 
                onClick={() => document.getElementById('fileInput')?.click()}
              >
                Вибрати файли
              </button>
            </div>

            <div style={{ marginTop: '16px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {mediaTypes.map((type) => (
                <button key={type.type} className="btn ghost" style={{ fontSize: '12px' }}>
                  {type.icon} {type.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {media.length > 0 ? (
          <div className="section" style={{ marginTop: '16px' }}>
            <div className="head">
              <h2>Медіа-бібліотека ({media.length})</h2>
            </div>
            <div className="body">
              <div className="grid">
                {media.map((item, idx) => (
                  <div 
                    key={idx} 
                    className="card"
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedMedia(item)}
                  >
                    <div style={{ 
                      height: '160px', 
                      background: 'rgba(11,15,20,.6)',
                      borderRadius: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '48px',
                      marginBottom: '12px'
                    }}>
                      {item.type === 'image' && '🖼️'}
                      {item.type === 'video' && '🎥'}
                      {item.type === 'audio' && '🎵'}
                      {item.type === 'document' && '📄'}
                    </div>
                    <h3 style={{ margin: '0 0 6px 0', fontSize: '14px' }}>
                      {item.title || 'Без назви'}
                    </h3>
                    <div className="sub" style={{ fontSize: '12px' }}>
                      {item.description || 'Немає опису'}
                    </div>
                    <div className="tags" style={{ marginTop: '8px' }}>
                      <span className="tag">{item.type}</span>
                      {item.size && <span className="tag">{item.size}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="section" style={{ marginTop: '16px' }}>
            <div className="head">
              <h2>Медіа-бібліотека</h2>
            </div>
            <div className="body">
              <div style={{ 
                textAlign: 'center', 
                padding: '40px',
                color: 'var(--muted)'
              }}>
                <div style={{ fontSize: '64px', marginBottom: '16px' }}>📦</div>
                <div style={{ fontSize: '16px' }}>
                  Галерея порожня
                </div>
                <div style={{ fontSize: '13px', marginTop: '8px' }}>
                  Завантажте перші файли, щоб почати
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {selectedMedia && (
        <div 
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,.85)',
            zIndex: 100,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
          }}
          onClick={() => setSelectedMedia(null)}
        >
          <div 
            style={{
              maxWidth: '800px',
              width: '100%',
              background: 'var(--panel)',
              border: '1px solid var(--stroke)',
              borderRadius: '22px',
              padding: '20px'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ margin: 0 }}>{selectedMedia.title || 'Медіа'}</h2>
              <button className="btn ghost" onClick={() => setSelectedMedia(null)}>
                ✕
              </button>
            </div>
            <div className="mono">
              {JSON.stringify(selectedMedia, null, 2)}
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        @import url('/ci.css');
      `}</style>
    </>
  );
}
