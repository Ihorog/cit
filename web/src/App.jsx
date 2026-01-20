import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_URL = 'http://localhost:8791';
const DB_NAME = 'cimeika_db';

class CimeikoDB {
  constructor() {
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('messages')) {
          db.createObjectStore('messages', { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }

  async addMessage(message) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('messages', 'readwrite');
      const store = tx.objectStore('messages');
      const request = store.add(message);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async getMessages() {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction('messages', 'readonly');
      const store = tx.objectStore('messages');
      const request = store.getAll();
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }
}

const ModuleCI = () => (
  <div className="module">
    <h2>🔄 Ci - Ядро оркестрації</h2>
    <p>Центр керування системою CIMEIKA</p>
    <div className="module-content">
      <div className="stat">
        <span>Статус:</span>
        <span style={{color: '#4caf50'}}>✓ Активна</span>
      </div>
      <div className="stat">
        <span>API:</span>
        <span style={{color: '#4f89ff'}}>http://localhost:8791</span>
      </div>
    </div>
  </div>
);

const ModuleKazkar = ({ messages, onSendMessage }) => (
  <div className="module">
    <h2>📚 Казкар - Памʼять і легенди</h2>
    <p>Спілкування з GPT-4.1</p>
    <div className="module-content chat-module">
      <div className="chat-log">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span>{msg.role === 'user' ? '👤' : '🤖'}</span>
            <span className="text">{msg.content}</span>
          </div>
        ))}
      </div>
      <MessageInput onSend={onSendMessage} />
    </div>
  </div>
);

const ModulePodia = () => (
  <div className="module">
    <h2>🎯 Подія - Майбутнє</h2>
    <p>Планування подій та сценарії</p>
    <div className="module-content">
      <div style={{padding: '16px', textAlign: 'center', color: '#b0b8c8'}}>
        Розроблюється...
      </div>
    </div>
  </div>
);

const ModuleNastrij = () => (
  <div className="module">
    <h2>💫 Настрій - Емоційний контекст</h2>
    <p>Статус та контекст системи</p>
    <div className="module-content">
      <div style={{padding: '16px', textAlign: 'center', color: '#b0b8c8'}}>
        Розроблюється...
      </div>
    </div>
  </div>
);

const ModuleMalia = () => (
  <div className="module">
    <h2>💡 Маля - Ідеї</h2>
    <p>Творче дослідження варіацій</p>
    <div className="module-content">
      <div style={{padding: '16px', textAlign: 'center', color: '#b0b8c8'}}>
        Розроблюється...
      </div>
    </div>
  </div>
);

const ModuleKalendar = () => (
  <div className="module">
    <h2>📅 Календар - Час</h2>
    <p>Часові вузлові точки</p>
    <div className="module-content">
      <div style={{padding: '16px', textAlign: 'center', color: '#b0b8c8'}}>
        Розроблюється...
      </div>
    </div>
  </div>
);

const ModuleGalerea = () => (
  <div className="module">
    <h2>🖼️ Галерея - Медіа архів</h2>
    <p>Зображення, відео, аудіо</p>
    <div className="module-content">
      <div style={{padding: '16px', textAlign: 'center', color: '#b0b8c8'}}>
        Розроблюється...
      </div>
    </div>
  </div>
);

const MessageInput = ({ onSend }) => {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSend(text);
      setText('');
    }
  };

  return (
    <div className="message-input">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Напиши щось..."
        onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
      />
      <button onClick={handleSend}>Отправити</button>
    </div>
  );
};

const Navigation = ({ activeModule, onSelectModule }) => {
  const modules = [
    { id: 'ci', emoji: '🔄' },
    { id: 'kazkar', emoji: '📚' },
    { id: 'podia', emoji: '🎯' },
    { id: 'nastrij', emoji: '💫' },
    { id: 'malia', emoji: '💡' },
    { id: 'kalendar', emoji: '📅' },
    { id: 'galerea', emoji: '🖼️' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-header">
        <h1>🌀 CIMEIKA</h1>
      </div>
      <div className="nav-modules">
        {modules.map((module) => (
          <button
            key={module.id}
            className={`nav-btn ${activeModule === module.id ? 'active' : ''}`}
            onClick={() => onSelectModule(module.id)}
            title={module.id}
          >
            <span className="emoji">{module.emoji}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};

const StatusBar = ({ isOnline, lastSync }) => (
  <div className="status-bar">
    <div>
      <span className={`status-dot ${isOnline ? 'online' : ''}`}></span>
      <span style={{marginLeft: '8px'}}>
        {isOnline ? 'На зв\'язку' : 'Offline'}
      </span>
    </div>
    <div style={{fontSize: '11px', opacity: 0.7}}>
      Синх: {lastSync ? new Date(lastSync).toLocaleTimeString('uk-UA') : 'Ніколи'}
    </div>
  </div>
);

export default function App() {
  const [activeModule, setActiveModule] = useState('ci');
  const [messages, setMessages] = useState([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastSync, setLastSync] = useState(null);
  const [db, setDb] = useState(null);

  useEffect(() => {
    const initDB = async () => {
      const database = new CimeikoDB();
      await database.init();
      setDb(database);
      const savedMessages = await database.getMessages();
      setMessages(savedMessages);
    };
    initDB();
  }, []);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleSendMessage = useCallback(
    async (text) => {
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };

      if (db) {
        await db.addMessage(userMessage);
      }
      setMessages((prev) => [...prev, userMessage]);

      if (isOnline) {
        try {
          const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }),
          });
          const data = await response.json();
          const aiMessage = {
            role: 'assistant',
            content: data.reply || 'Помилка',
            timestamp: new Date().toISOString(),
          };
          if (db) {
            await db.addMessage(aiMessage);
          }
          setMessages((prev) => [...prev, aiMessage]);
          setLastSync(new Date());
        } catch (error) {
          console.error('API Error:', error);
        }
      }
    },
    [db, isOnline]
  );

  const renderModule = () => {
    switch (activeModule) {
      case 'ci': return <ModuleCI />;
      case 'kazkar': return <ModuleKazkar messages={messages} onSendMessage={handleSendMessage} />;
      case 'podia': return <ModulePodia />;
      case 'nastrij': return <ModuleNastrij />;
      case 'malia': return <ModuleMalia />;
      case 'kalendar': return <ModuleKalendar />;
      case 'galerea': return <ModuleGalerea />;
      default: return <ModuleCI />;
    }
  };

  return (
    <div className="app">
      <Navigation activeModule={activeModule} onSelectModule={setActiveModule} />
      <main className="main-content">{renderModule()}</main>
      <StatusBar isOnline={isOnline} lastSync={lastSync} />
    </div>
  );
}
