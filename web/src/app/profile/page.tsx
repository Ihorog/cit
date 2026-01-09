'use client';

import { useState, useEffect } from 'react';

interface Profile {
  name: string;
  email: string;
  bio: string;
  avatar: string;
  interests: string[];
  createdAt: string;
  updatedAt?: string;
}

export default function ProfilePage() {
  const [health, setHealth] = useState<string>('...');
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isEditing, setIsEditing] = useState(false);
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

  const getDefaultProfile = (): Profile => ({
    name: '',
    email: '',
    bio: '',
    avatar: '👤',
    interests: [],
    createdAt: new Date().toISOString()
  });

  const loadProfile = async () => {
    try {
      const res = await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.get',
          input: { node_id: 'profile', key: 'user_profile' }
        })
      });
      const data = await res.json();
      if (data.result?.value) {
        setProfile(JSON.parse(data.result.value));
      } else {
        setProfile(getDefaultProfile());
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
      setProfile(getDefaultProfile());
    }
  };

  const saveProfile = async (updatedProfile: Profile) => {
    try {
      await fetch(`${API}/api/exec`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'actions.state.set',
          input: { 
            node_id: 'profile', 
            key: 'user_profile',
            value: JSON.stringify({
              ...updatedProfile,
              updatedAt: new Date().toISOString()
            })
          }
        })
      });
      
      setProfile({
        ...updatedProfile,
        updatedAt: new Date().toISOString()
      });
      setIsEditing(false);
    } catch (err) {
      console.error('Failed to save profile:', err);
    }
  };

  useEffect(() => {
    checkHealth();
    loadProfile();
  }, []);

  const avatarOptions = ['👤', '😊', '🧑', '👨', '👩', '🧔', '👱', '🧑‍💻', '🎨', '📚', '🎵', '⚽', '🎮'];
  const interestOptions = [
    { value: 'технології', label: '💻 Технології' },
    { value: 'творчість', label: '🎨 Творчість' },
    { value: 'музика', label: '🎵 Музика' },
    { value: 'спорт', label: '⚽ Спорт' },
    { value: 'навчання', label: '📚 Навчання' },
    { value: 'подорожі', label: '✈️ Подорожі' },
    { value: 'кулінарія', label: '🍳 Кулінарія' },
    { value: 'фотографія', label: '📷 Фотографія' }
  ];

  if (!profile) {
    return (
      <>
        <div className="topbar">
          <div className="brand">
            <div className="title">Профіль</div>
          </div>
        </div>
        <div className="wrap">
          <div className="section">
            <div className="body">
              <div className="mono">Завантаження профілю...</div>
            </div>
          </div>
        </div>
        <style jsx global>{`
          @import url('/ci.css');
        `}</style>
      </>
    );
  }

  return (
    <>
      <div className="topbar">
        <div className="brand">
          <div className="title">Профіль</div>
          <div className="pills">
            <span className="pill">особистий кабінет</span>
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
            <h2>Профіль користувача</h2>
          </div>
          <div className="body">
            <div className="mono">
              Профіль — особистий кабінет (я).
              {'\n\n'}
              Керування особистими даними та налаштуваннями.
            </div>
          </div>
        </div>

        {!isEditing ? (
          <>
            <div className="section" style={{ marginTop: '16px' }}>
              <div className="head">
                <h2>Мої дані</h2>
                <button className="btn" onClick={() => setIsEditing(true)}>
                  Редагувати
                </button>
              </div>
              <div className="body">
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                  <div style={{ 
                    fontSize: '64px', 
                    width: '80px', 
                    height: '80px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    background: 'rgba(31,164,255,.15)',
                    borderRadius: '50%',
                    border: '2px solid var(--stroke)'
                  }}>
                    {profile.avatar || '👤'}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '24px' }}>
                      {profile.name || 'Не вказано'}
                    </h3>
                    {profile.email && (
                      <div style={{ color: 'var(--muted)', fontSize: '14px', marginBottom: '4px' }}>
                        {profile.email}
                      </div>
                    )}
                  </div>
                </div>

                {profile.bio && (
                  <div style={{ marginBottom: '20px' }}>
                    <div style={{ fontSize: '13px', color: 'var(--muted)', marginBottom: '8px' }}>
                      Про себе
                    </div>
                    <div style={{ 
                      padding: '12px', 
                      background: 'rgba(15,22,32,.6)', 
                      borderRadius: '12px',
                      border: '1px solid var(--stroke)'
                    }}>
                      {profile.bio}
                    </div>
                  </div>
                )}

                {profile.interests && profile.interests.length > 0 && (
                  <div>
                    <div style={{ fontSize: '13px', color: 'var(--muted)', marginBottom: '8px' }}>
                      Інтереси
                    </div>
                    <div className="tags">
                      {profile.interests.map((interest) => {
                        const interestData = interestOptions.find(opt => opt.value === interest);
                        return (
                          <span key={interest} className="tag" style={{ 
                            background: 'rgba(31,164,255,.20)',
                            borderColor: 'rgba(31,164,255,.35)',
                            color: 'var(--text)'
                          }}>
                            {interestData?.label || interest}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}

                {profile.createdAt && (
                  <div style={{ 
                    marginTop: '24px', 
                    paddingTop: '16px', 
                    borderTop: '1px solid var(--stroke)',
                    fontSize: '11px',
                    color: 'var(--muted)'
                  }}>
                    Профіль створено: {new Date(profile.createdAt).toLocaleDateString('uk-UA')}
                    {profile.updatedAt && (
                      <span> • Оновлено: {new Date(profile.updatedAt).toLocaleDateString('uk-UA')}</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="section" style={{ marginTop: '16px' }}>
            <div className="head">
              <h2>Редагування профілю</h2>
            </div>
            <div className="body">
              <form key={profile.updatedAt || profile.createdAt} onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const interests = formData.getAll('interests') as string[];
                saveProfile({
                  ...profile,
                  name: formData.get('name') as string,
                  email: formData.get('email') as string,
                  bio: formData.get('bio') as string,
                  avatar: formData.get('avatar') as string,
                  interests
                });
              }}>
                <div style={{ display: 'grid', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--muted)' }}>
                      Аватар
                    </label>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {avatarOptions.map((emoji) => (
                        <label key={emoji} style={{ cursor: 'pointer' }}>
                          <input 
                            type="radio" 
                            name="avatar" 
                            value={emoji} 
                            defaultChecked={profile.avatar === emoji}
                            style={{ display: 'none' }}
                          />
                          <div style={{ 
                            fontSize: '32px', 
                            padding: '8px',
                            border: '2px solid var(--stroke)',
                            borderRadius: '8px',
                            background: 'rgba(15,22,32,.6)',
                            transition: 'all 0.2s'
                          }}
                          className="avatar-option"
                          >
                            {emoji}
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Ім'я
                    </label>
                    <input 
                      type="text" 
                      name="name" 
                      placeholder="Ваше ім'я" 
                      defaultValue={profile.name}
                      required 
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Email
                    </label>
                    <input 
                      type="email" 
                      name="email" 
                      placeholder="your@email.com" 
                      defaultValue={profile.email}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', color: 'var(--muted)' }}>
                      Про себе
                    </label>
                    <textarea 
                      name="bio" 
                      placeholder="Розкажіть про себе..." 
                      rows={4}
                      defaultValue={profile.bio}
                    />
                  </div>

                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', color: 'var(--muted)' }}>
                      Інтереси
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '8px' }}>
                      {interestOptions.map((interest) => (
                        <label key={interest.value} style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '8px',
                          padding: '10px 12px',
                          background: 'rgba(15,22,32,.6)',
                          border: '1px solid var(--stroke)',
                          borderRadius: '8px',
                          cursor: 'pointer'
                        }}>
                          <input 
                            type="checkbox" 
                            name="interests" 
                            value={interest.value}
                            defaultChecked={profile.interests?.includes(interest.value)}
                          />
                          <span style={{ fontSize: '13px' }}>{interest.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                    <button type="submit" className="btn" style={{ flex: 1 }}>
                      Зберегти
                    </button>
                    <button 
                      type="button" 
                      className="btn ghost" 
                      onClick={() => setIsEditing(false)}
                      style={{ flex: 1 }}
                    >
                      Скасувати
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        @import url('/ci.css');
        
        .avatar-option:hover {
          border-color: var(--blue) !important;
          background: rgba(31,164,255,.15) !important;
        }
        
        input[type="radio"]:checked + .avatar-option {
          border-color: var(--blue) !important;
          background: rgba(31,164,255,.25) !important;
          box-shadow: 0 0 0 2px rgba(31,164,255,.15);
        }
      `}</style>
    </>
  );
}
