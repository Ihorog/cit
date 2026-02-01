#!/usr/bin/env python3
"""
Ci — Домашній AI асистент
Єдиний самовиконуваний файл для Termux та Windows

Запуск:
  python ci.py

Відкрий у браузері:
  http://localhost:8790
"""

import os
import sys
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError
from pathlib import Path
import base64
import time
from datetime import datetime, timezone

# Імпорт модуля аудиту
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from core.audit import get_audit_instance
    AUDIT_ENABLED = True
except ImportError:
    AUDIT_ENABLED = False
    print("[WARNING] Audit module not available")

# ============ Утиліти ============
def now_utc_iso():
    """Return current UTC time in ISO 8601 format"""
    return datetime.now(timezone.utc).isoformat()

# ============ Конфігурація ============
HOST = "0.0.0.0"
PORT = 8790
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
DATA_DIR = Path.home() / ".ci-data"

# ============ Іконка (base64 PNG) ============
ICON_BASE64 = "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"

# ============ HTML UI (вбудований) ============
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="theme-color" content="#1a1a1a">
  <title>Ci · Домашній асистент</title>
  <link rel="icon" type="image/png" href="/icon.png">
  <style>
    :root {
      --bg-primary: #1a1a1a;
      --bg-secondary: #242424;
      --bg-tertiary: #2a2a2a;
      --bg-hover: #333;
      --text-primary: #e8e8e8;
      --text-secondary: #a0a0a0;
      --text-muted: #666;
      --accent: #7c6aef;
      --accent-hover: #9080ff;
      --accent-dim: rgba(124, 106, 239, 0.15);
      --border: #333;
      --user-bubble: #2d5a4a;
      --danger: #e74c3c;
      --success: #27ae60;
      --warning: #f39c12;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    html, body { height: 100%; overflow: hidden; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      display: flex;
      flex-direction: column;
    }
    
    /* Header */
    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 1rem;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
    }
    .header-left { display: flex; align-items: center; gap: 0.75rem; }
    .icon-btn {
      background: none;
      border: none;
      color: var(--text-primary);
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 8px;
      display: flex;
      transition: background 0.2s;
    }
    .icon-btn:hover { background: var(--bg-hover); }
    .icon-btn svg { width: 24px; height: 24px; }
    .logo {
      font-size: 1.25rem;
      font-weight: 600;
      background: linear-gradient(135deg, var(--accent) 0%, #a890ff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .new-chat-btn {
      background: var(--accent);
      border: none;
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
    }
    .new-chat-btn:hover { background: var(--accent-hover); }

    /* Sidebar */
    .sidebar-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      z-index: 100;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.3s, visibility 0.3s;
    }
    .sidebar-overlay.open { opacity: 1; visibility: visible; }
    .sidebar {
      position: fixed;
      left: 0;
      top: 0;
      bottom: 0;
      width: 300px;
      max-width: 85vw;
      background: var(--bg-secondary);
      z-index: 101;
      transform: translateX(-100%);
      transition: transform 0.3s ease;
      display: flex;
      flex-direction: column;
    }
    .sidebar.open { transform: translateX(0); }
    .sidebar-header {
      padding: 1rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .sidebar-title { font-weight: 600; }
    .sidebar-content { flex: 1; overflow-y: auto; padding: 0.5rem; }
    .chat-list { display: flex; flex-direction: column; gap: 2px; }
    .chat-item {
      padding: 0.75rem 1rem;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      transition: background 0.2s;
    }
    .chat-item:hover { background: var(--bg-hover); }
    .chat-item.active { background: var(--bg-tertiary); }
    .chat-item-content { flex: 1; min-width: 0; }
    .chat-item-title {
      font-size: 0.875rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .chat-item-date { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }
    .chat-item-delete {
      opacity: 0;
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
    }
    .chat-item:hover .chat-item-delete { opacity: 1; }
    .chat-item-delete:hover { color: var(--danger); }
    .sidebar-section { padding: 1rem; border-top: 1px solid var(--border); }
    .sidebar-section-title {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.75rem;
    }
    .sidebar-btn {
      width: 100%;
      padding: 0.75rem;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-primary);
      font-size: 0.875rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.5rem;
    }
    .sidebar-btn:hover { background: var(--bg-hover); }
    .sidebar-btn svg { width: 18px; height: 18px; flex-shrink: 0; }
    .sidebar-btn.danger:hover {
      background: rgba(231, 76, 60, 0.15);
      border-color: var(--danger);
      color: var(--danger);
    }
    .api-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.5rem 0.75rem;
      background: var(--accent-dim);
      border-radius: 6px;
      font-size: 0.8125rem;
      margin-bottom: 0.75rem;
    }
    .api-status.error { background: rgba(231, 76, 60, 0.15); color: var(--danger); }
    .api-status svg { width: 16px; height: 16px; }
    .empty-state {
      text-align: center;
      padding: 2rem 1rem;
      color: var(--text-muted);
      font-size: 0.875rem;
    }

    /* Messages */
    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
      display: flex;
      flex-direction: column;
    }
    .messages-wrapper {
      max-width: 800px;
      width: 100%;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .welcome-screen {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      padding: 2rem;
    }
    .welcome-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, var(--accent) 0%, #a890ff 100%);
      border-radius: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 1.5rem;
      font-size: 2.5rem;
    }
    .welcome-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem; }
    .welcome-subtitle { color: var(--text-secondary); max-width: 400px; }
    .message { display: flex; gap: 1rem; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .message-avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: 1rem;
    }
    .message.user .message-avatar { background: var(--user-bubble); }
    .message.assistant .message-avatar {
      background: linear-gradient(135deg, var(--accent) 0%, #a890ff 100%);
    }
    .message-content { flex: 1; min-width: 0; }
    .message-sender {
      font-size: 0.8125rem;
      font-weight: 600;
      margin-bottom: 0.375rem;
      color: var(--text-secondary);
    }
    .message-text { font-size: 0.9375rem; line-height: 1.6; word-wrap: break-word; }
    .message-text p { margin-bottom: 0.75rem; }
    .message-text p:last-child { margin-bottom: 0; }
    .message-text code {
      background: var(--bg-tertiary);
      padding: 0.125rem 0.375rem;
      border-radius: 4px;
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 0.875em;
    }
    .message-text pre {
      background: var(--bg-tertiary);
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      margin: 0.75rem 0;
    }
    .message-text pre code { background: none; padding: 0; }
    .message-text ul, .message-text ol { margin: 0.5rem 0; padding-left: 1.5rem; }
    .message-actions {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.5rem;
      opacity: 0;
      transition: opacity 0.2s;
    }
    .message:hover .message-actions { opacity: 1; }
    .action-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
      border-radius: 4px;
      display: flex;
    }
    .action-btn:hover { color: var(--text-primary); background: var(--bg-hover); }
    .action-btn svg { width: 16px; height: 16px; }

    /* Typing Indicator */
    .typing-indicator { display: none; gap: 1rem; }
    .typing-indicator.visible { display: flex; }
    .typing-dots { display: flex; gap: 4px; padding: 0.75rem 0; }
    .typing-dots span {
      width: 8px;
      height: 8px;
      background: var(--text-muted);
      border-radius: 50%;
      animation: bounce 1.4s infinite ease-in-out;
    }
    .typing-dots span:nth-child(1) { animation-delay: 0s; }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
      40% { transform: scale(1); opacity: 1; }
    }

    /* Input */
    .input-container {
      padding: 1rem;
      background: var(--bg-primary);
      border-top: 1px solid var(--border);
      flex-shrink: 0;
    }
    .input-wrapper { max-width: 800px; margin: 0 auto; }
    .input-box {
      display: flex;
      align-items: flex-end;
      gap: 0.5rem;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 0.5rem;
      transition: border-color 0.2s;
    }
    .input-box:focus-within { border-color: var(--accent); }
    .attach-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 8px;
      display: flex;
      flex-shrink: 0;
    }
    .attach-btn:hover { color: var(--text-primary); background: var(--bg-hover); }
    .attach-btn svg { width: 20px; height: 20px; }
    #message-input {
      flex: 1;
      background: none;
      border: none;
      color: var(--text-primary);
      font-family: inherit;
      font-size: 0.9375rem;
      line-height: 1.5;
      resize: none;
      outline: none;
      max-height: 200px;
      min-height: 24px;
      padding: 0.375rem 0;
    }
    #message-input::placeholder { color: var(--text-muted); }
    .send-btn {
      background: var(--accent);
      border: none;
      color: white;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 8px;
      display: flex;
      flex-shrink: 0;
    }
    .send-btn:hover { background: var(--accent-hover); }
    .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .send-btn svg { width: 20px; height: 20px; }
    .status-bar {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.5rem;
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success);
    }
    .status-dot.offline { background: var(--danger); }
    .status-dot.syncing { background: var(--warning); animation: pulse 1s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    #file-input { display: none; }
    .attached-files { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem; }
    .attached-file {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--bg-tertiary);
      padding: 0.375rem 0.75rem;
      border-radius: 8px;
      font-size: 0.8125rem;
    }
    .attached-file-remove {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 2px;
      display: flex;
    }
    .attached-file-remove:hover { color: var(--danger); }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* Toast */
    .toast-container {
      position: fixed;
      bottom: 100px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 300;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
    .toast {
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      font-size: 0.875rem;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: toastIn 0.3s ease;
    }
    .toast.success { border-color: var(--success); }
    .toast.error { border-color: var(--danger); }
    @keyframes toastIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Settings Modal */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.7);
      z-index: 200;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.3s, visibility 0.3s;
    }
    .modal-overlay.open { opacity: 1; visibility: visible; }
    .modal {
      background: var(--bg-secondary);
      border-radius: 16px;
      width: 100%;
      max-width: 450px;
      max-height: 90vh;
      overflow-y: auto;
      transform: scale(0.95);
      transition: transform 0.3s;
    }
    .modal-overlay.open .modal { transform: scale(1); }
    .modal-header {
      padding: 1.25rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-title { font-size: 1.125rem; font-weight: 600; }
    .modal-body { padding: 1.25rem; }
    .form-group { margin-bottom: 1.25rem; }
    .form-group:last-child { margin-bottom: 0; }
    .form-label { display: block; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem; }
    .form-hint { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.375rem; }
    .form-input {
      width: 100%;
      padding: 0.75rem;
      background: var(--bg-tertiary);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-primary);
      font-family: inherit;
      font-size: 0.9375rem;
      outline: none;
    }
    .form-input:focus { border-color: var(--accent); }
    .form-input::placeholder { color: var(--text-muted); }
    .modal-footer {
      padding: 1rem 1.25rem;
      border-top: 1px solid var(--border);
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
    }
    .btn {
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      border: none;
    }
    .btn-primary { background: var(--accent); color: white; }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-secondary {
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { background: var(--bg-hover); }
  </style>
</head>
<body>
  <div class="sidebar-overlay" id="sidebar-overlay"></div>
  
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Меню</span>
      <button class="icon-btn" id="close-sidebar">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div class="sidebar-content">
      <div class="sidebar-section" style="border-top: none; padding-top: 0.5rem;">
        <div class="sidebar-section-title">API Статус</div>
        <div class="api-status" id="api-status">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
          <span id="api-status-text">Перевірка...</span>
        </div>
      </div>
      <div class="sidebar-section">
        <div class="sidebar-section-title">Історія чатів</div>
        <div class="chat-list" id="chat-list">
          <div class="empty-state">Немає збережених чатів</div>
        </div>
      </div>
    </div>
    <div class="sidebar-section">
      <button class="sidebar-btn" id="settings-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
        Налаштування
      </button>
      <button class="sidebar-btn danger" id="clear-all-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14"/></svg>
        Очистити історію
      </button>
    </div>
  </aside>

  <div class="modal-overlay" id="settings-modal">
    <div class="modal">
      <div class="modal-header">
        <h2 class="modal-title">Налаштування</h2>
        <button class="icon-btn" id="close-settings">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">OpenAI API ключ</label>
          <input type="password" class="form-input" id="api-key-input" placeholder="sk-...">
          <p class="form-hint">Зберігається локально на сервері</p>
        </div>
        <div class="form-group">
          <label class="form-label">Модель</label>
          <input type="text" class="form-input" id="model-input" placeholder="gpt-4o-mini">
        </div>
        <div class="form-group">
          <label class="form-label">Ім'я користувача</label>
          <input type="text" class="form-input" id="username-input" placeholder="Ви">
        </div>
        <div class="form-group">
          <label class="form-label">Ім'я асистента</label>
          <input type="text" class="form-input" id="assistant-name-input" placeholder="Ci">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" id="cancel-settings">Скасувати</button>
        <button class="btn btn-primary" id="save-settings">Зберегти</button>
      </div>
    </div>
  </div>

  <header class="header">
    <div class="header-left">
      <button class="icon-btn" id="menu-btn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
      </button>
      <span class="logo" id="app-logo">Ci</span>
    </div>
    <button class="new-chat-btn" id="new-chat-btn">+ Новий</button>
  </header>

  <main class="messages-container" id="messages-container">
    <div class="messages-wrapper" id="messages-wrapper">
      <div class="welcome-screen" id="welcome-screen">
        <div class="welcome-icon">🏠</div>
        <h1 class="welcome-title">Вітаю!</h1>
        <p class="welcome-subtitle">Я Ci — твій домашній асистент. Чим можу допомогти?</p>
      </div>
    </div>
    <div class="messages-wrapper">
      <div class="typing-indicator" id="typing-indicator">
        <div class="message-avatar" style="background: linear-gradient(135deg, var(--accent) 0%, #a890ff 100%);">🤖</div>
        <div class="message-content">
          <div class="typing-dots"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>
  </main>

  <footer class="input-container">
    <div class="input-wrapper">
      <div class="attached-files" id="attached-files"></div>
      <div class="input-box">
        <button class="attach-btn" id="attach-btn" title="Прикріпити файл">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
        </button>
        <input type="file" id="file-input" multiple>
        <textarea id="message-input" placeholder="Напиши повідомлення..." rows="1"></textarea>
        <button class="send-btn" id="send-btn" title="Надіслати">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
        </button>
      </div>
      <div class="status-bar">
        <span class="status-dot" id="status-dot"></span>
        <span id="status-text">Підключено</span>
      </div>
    </div>
  </footer>

  <div class="toast-container" id="toast-container"></div>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const STORAGE_KEY = 'ci_data';
    let chats = [];
    let currentChatId = null;
    let attachedFiles = [];
    let settings = { username: 'Ви', assistantName: 'Ci', apiKey: '', model: 'gpt-4o-mini' };

    const $ = id => document.getElementById(id);
    const menuBtn = $('menu-btn');
    const sidebar = $('sidebar');
    const sidebarOverlay = $('sidebar-overlay');
    const closeSidebarBtn = $('close-sidebar');
    const newChatBtn = $('new-chat-btn');
    const chatList = $('chat-list');
    const clearAllBtn = $('clear-all-btn');
    const settingsBtn = $('settings-btn');
    const settingsModal = $('settings-modal');
    const closeSettingsBtn = $('close-settings');
    const cancelSettingsBtn = $('cancel-settings');
    const saveSettingsBtn = $('save-settings');
    const apiKeyInput = $('api-key-input');
    const modelInput = $('model-input');
    const usernameInput = $('username-input');
    const assistantNameInput = $('assistant-name-input');
    const messagesContainer = $('messages-container');
    const messagesWrapper = $('messages-wrapper');
    const welcomeScreen = $('welcome-screen');
    const typingIndicator = $('typing-indicator');
    const messageInput = $('message-input');
    const sendBtn = $('send-btn');
    const attachBtn = $('attach-btn');
    const fileInput = $('file-input');
    const attachedFilesContainer = $('attached-files');
    const statusDot = $('status-dot');
    const statusText = $('status-text');
    const appLogo = $('app-logo');
    const toastContainer = $('toast-container');
    const apiStatus = $('api-status');
    const apiStatusText = $('api-status-text');

    function generateId() { return Date.now().toString(36) + Math.random().toString(36).substr(2); }
    
    function formatDate(ts) {
      const d = new Date(ts), now = new Date(), diff = now - d;
      if (diff < 60000) return 'Щойно';
      if (diff < 3600000) return `${Math.floor(diff / 60000)} хв тому`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)} год тому`;
      return d.toLocaleDateString('uk', { day: 'numeric', month: 'short' });
    }
    
    function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
    
    function showToast(msg, type = 'info') {
      const t = document.createElement('div');
      t.className = `toast ${type}`;
      t.textContent = msg;
      toastContainer.appendChild(t);
      setTimeout(() => t.remove(), 3000);
    }

    function loadData() {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const data = JSON.parse(stored);
          chats = data.chats || [];
          settings = { ...settings, ...data.settings };
        }
      } catch (e) { console.error(e); }
      applySettings();
    }

    function saveData() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ chats, settings }));
    }

    function applySettings() {
      appLogo.textContent = settings.assistantName;
      apiKeyInput.value = settings.apiKey;
      modelInput.value = settings.model;
      usernameInput.value = settings.username;
      assistantNameInput.value = settings.assistantName;
    }

    function openSettings() { applySettings(); settingsModal.classList.add('open'); }
    function closeSettings() { settingsModal.classList.remove('open'); }
    
    async function saveSettings() {
      settings.apiKey = apiKeyInput.value.trim();
      settings.model = modelInput.value.trim() || 'gpt-4o-mini';
      settings.username = usernameInput.value.trim() || 'Ви';
      settings.assistantName = assistantNameInput.value.trim() || 'Ci';
      
      // Save to server
      try {
        await fetch('/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ apiKey: settings.apiKey, model: settings.model })
        });
      } catch (e) {}
      
      saveData();
      applySettings();
      closeSettings();
      showToast('Налаштування збережено', 'success');
      checkApiStatus();
    }

    function createNewChat() {
      const chat = { id: generateId(), title: 'Новий чат', messages: [], createdAt: Date.now(), updatedAt: Date.now() };
      chats.unshift(chat);
      saveData();
      selectChat(chat.id);
      renderChatList();
      closeSidebar();
    }

    function selectChat(id) { currentChatId = id; renderMessages(); renderChatList(); }

    function deleteChat(id, e) {
      e.stopPropagation();
      chats = chats.filter(c => c.id !== id);
      saveData();
      if (currentChatId === id) {
        currentChatId = chats.length > 0 ? chats[0].id : null;
        renderMessages();
      }
      renderChatList();
    }

    function clearAllChats() {
      if (!confirm('Видалити всю історію чатів?')) return;
      chats = [];
      currentChatId = null;
      saveData();
      renderChatList();
      renderMessages();
      closeSidebar();
      showToast('Історію очищено', 'success');
    }

    function getCurrentChat() { return chats.find(c => c.id === currentChatId); }

    function updateChatTitle(chat) {
      if (chat.messages.length === 1) {
        const m = chat.messages[0].content;
        chat.title = m.length > 40 ? m.substring(0, 40) + '...' : m;
        saveData();
        renderChatList();
      }
    }

    function renderChatList() {
      if (chats.length === 0) {
        chatList.innerHTML = '<div class="empty-state">Немає збережених чатів</div>';
        return;
      }
      chatList.innerHTML = chats.map(c => `
        <div class="chat-item ${c.id === currentChatId ? 'active' : ''}" data-id="${c.id}">
          <div class="chat-item-content">
            <div class="chat-item-title">${escapeHtml(c.title)}</div>
            <div class="chat-item-date">${formatDate(c.updatedAt)}</div>
          </div>
          <button class="chat-item-delete" data-id="${c.id}">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      `).join('');
      chatList.querySelectorAll('.chat-item').forEach(el => {
        el.addEventListener('click', () => { selectChat(el.dataset.id); closeSidebar(); });
      });
      chatList.querySelectorAll('.chat-item-delete').forEach(el => {
        el.addEventListener('click', (e) => deleteChat(el.dataset.id, e));
      });
    }

    function renderMessages() {
      const chat = getCurrentChat();
      if (!chat || chat.messages.length === 0) {
        welcomeScreen.style.display = 'flex';
        messagesWrapper.innerHTML = '';
        messagesWrapper.appendChild(welcomeScreen);
        return;
      }
      welcomeScreen.style.display = 'none';
      messagesWrapper.innerHTML = chat.messages.map((m, i) => `
        <div class="message ${m.role}">
          <div class="message-avatar">${m.role === 'user' ? '👤' : '🤖'}</div>
          <div class="message-content">
            <div class="message-sender">${m.role === 'user' ? escapeHtml(settings.username) : escapeHtml(settings.assistantName)}</div>
            <div class="message-text">${marked.parse(m.content)}</div>
            <div class="message-actions">
              <button class="action-btn copy-btn" data-index="${i}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>
              </button>
            </div>
          </div>
        </div>
      `).join('');
      messagesWrapper.querySelectorAll('.copy-btn').forEach(b => {
        b.addEventListener('click', () => {
          navigator.clipboard.writeText(chat.messages[parseInt(b.dataset.index)].content);
          showToast('Скопійовано', 'success');
        });
      });
      scrollToBottom();
    }

    function scrollToBottom() { messagesContainer.scrollTop = messagesContainer.scrollHeight; }
    function openSidebar() { sidebar.classList.add('open'); sidebarOverlay.classList.add('open'); }
    function closeSidebar() { sidebar.classList.remove('open'); sidebarOverlay.classList.remove('open'); }

    function handleFiles(files) {
      for (const f of files) { if (attachedFiles.length >= 5) break; attachedFiles.push(f); }
      renderAttachedFiles();
    }

    function removeFile(i) { attachedFiles.splice(i, 1); renderAttachedFiles(); }

    function renderAttachedFiles() {
      if (attachedFiles.length === 0) { attachedFilesContainer.innerHTML = ''; return; }
      attachedFilesContainer.innerHTML = attachedFiles.map((f, i) => `
        <div class="attached-file">
          <span>📎 ${escapeHtml(f.name)}</span>
          <button class="attached-file-remove" data-index="${i}">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      `).join('');
      attachedFilesContainer.querySelectorAll('.attached-file-remove').forEach(b => {
        b.addEventListener('click', () => removeFile(parseInt(b.dataset.index)));
      });
    }

    async function sendMessage() {
      const text = messageInput.value.trim();
      if (!text) return;
      if (!currentChatId) createNewChat();
      const chat = getCurrentChat();
      
      chat.messages.push({ role: 'user', content: text, timestamp: Date.now() });
      chat.updatedAt = Date.now();
      updateChatTitle(chat);
      saveData();
      renderMessages();

      messageInput.value = '';
      messageInput.style.height = 'auto';
      attachedFiles = [];
      renderAttachedFiles();

      typingIndicator.classList.add('visible');
      scrollToBottom();

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: chat.messages.map(m => ({ role: m.role, content: m.content })) })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        // Support both old format (data.choices) and new format (data.reply)
        const reply = data.reply || data.choices?.[0]?.message?.content || 'Немає відповіді';
        chat.messages.push({ role: 'assistant', content: reply, timestamp: Date.now() });
        setStatus(true);
      } catch (err) {
        chat.messages.push({ role: 'assistant', content: `⚠️ Помилка: ${err.message}`, timestamp: Date.now() });
        setStatus(false);
      }
      
      chat.updatedAt = Date.now();
      saveData();
      typingIndicator.classList.remove('visible');
      renderMessages();
    }

    async function checkApiStatus() {
      try {
        const res = await fetch('/health');
        const data = await res.json();
        // Support both old format (api_configured) and new format (openai)
        const apiConfigured = data.openai !== undefined ? data.openai : data.api_configured;
        if (apiConfigured) {
          apiStatus.classList.remove('error');
          apiStatusText.textContent = `API: ${data.model}`;
          setStatus(true);
        } else {
          apiStatus.classList.add('error');
          apiStatusText.textContent = 'API ключ не налаштовано';
          setStatus(false);
        }
      } catch {
        apiStatus.classList.add('error');
        apiStatusText.textContent = 'Сервер недоступний';
        setStatus(false);
      }
    }

    function setStatus(online) {
      statusDot.className = 'status-dot' + (online ? '' : ' offline');
      statusText.textContent = online ? 'Підключено' : 'Офлайн';
    }

    function autoResize() {
      messageInput.style.height = 'auto';
      messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
    }

    // Events
    menuBtn.addEventListener('click', openSidebar);
    sidebarOverlay.addEventListener('click', closeSidebar);
    closeSidebarBtn.addEventListener('click', closeSidebar);
    newChatBtn.addEventListener('click', createNewChat);
    clearAllBtn.addEventListener('click', clearAllChats);
    settingsBtn.addEventListener('click', openSettings);
    closeSettingsBtn.addEventListener('click', closeSettings);
    cancelSettingsBtn.addEventListener('click', closeSettings);
    saveSettingsBtn.addEventListener('click', saveSettings);
    settingsModal.addEventListener('click', (e) => { if (e.target === settingsModal) closeSettings(); });
    attachBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => { handleFiles(e.target.files); fileInput.value = ''; });
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('input', autoResize);
    messageInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });

    // Init
    loadData();
    renderChatList();
    if (chats.length > 0) currentChatId = chats[0].id;
    renderMessages();
    checkApiStatus();
    setInterval(checkApiStatus, 30000);
    marked.setOptions({ breaks: true, gfm: true });
  </script>
</body>
</html>'''

# ============ HTTP Handler ============
class CiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        start_time = time.time()
        status_code = 200
        
        # Отримати шлях без query string для порівняння
        path_only = self.path.split("?")[0]
        
        try:
            if path_only == "/" or path_only == "/index.html":
                self.send_html(HTML_TEMPLATE)
            elif path_only == "/icon.png":
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                self.wfile.write(base64.b64decode(ICON_BASE64))
            elif path_only == "/health":
                self.send_json({
                    "ok": True,
                    "service": "cit",
                    "time": now_utc_iso(),
                    "port": PORT,
                    "model": OPENAI_MODEL,
                    "openai": bool(OPENAI_API_KEY)
                })
            elif path_only == "/audit":
                self.handle_audit_report()
            elif path_only == "/audit/resources":
                self.handle_audit_resources()
            else:
                status_code = 404
                self.send_response(404)
                self.end_headers()
        finally:
            # Аудит запиту
            if AUDIT_ENABLED:
                try:
                    audit = get_audit_instance()
                    response_time = (time.time() - start_time) * 1000
                    audit.audit_api_request(
                        method="GET",
                        path=self.path,
                        client_ip=self.client_address[0],
                        user_agent=self.headers.get("User-Agent", ""),
                        status_code=status_code,
                        response_time_ms=response_time
                    )
                except Exception as e:
                    print(f"[WARNING] Audit logging failed: {e}")

    def do_POST(self):
        start_time = time.time()
        status_code = 200
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            status_code = 400
            self.send_json({"error": "Invalid JSON"}, 400)
            return
        finally:
            # Аудит запиту
            if AUDIT_ENABLED:
                try:
                    audit = get_audit_instance()
                    response_time = (time.time() - start_time) * 1000
                    audit.audit_api_request(
                        method="POST",
                        path=self.path,
                        client_ip=self.client_address[0],
                        user_agent=self.headers.get("User-Agent", ""),
                        status_code=status_code,
                        response_time_ms=response_time
                    )
                except Exception as e:
                    print(f"[WARNING] Audit logging failed: {e}")

        if self.path == "/chat":
            self.handle_chat(data)
        elif self.path == "/settings":
            self.handle_settings(data)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_chat(self, data):
        global OPENAI_API_KEY, OPENAI_MODEL
        
        if not OPENAI_API_KEY:
            self.send_json({"error": "API ключ не налаштовано. Відкрий налаштування."}, 400)
            return

        messages = data.get("messages", [])
        
        # Handle empty message gracefully - check if no messages or all messages are empty
        if not messages:
            self.send_json({
                "ok": True,
                "cit": "v1",
                "time": now_utc_iso(),
                "model": OPENAI_MODEL,
                "reply": "Send me a message to start chatting!",
                "api": "system",
                "raw": None
            })
            return
        
        if all(not msg.get("content", "").strip() for msg in messages):
            self.send_json({
                "ok": True,
                "cit": "v1",
                "time": now_utc_iso(),
                "model": OPENAI_MODEL,
                "reply": "Send me a message to start chatting!",
                "api": "system",
                "raw": None
            })
            return
        
        try:
            req_data = json.dumps({
                "model": OPENAI_MODEL,
                "messages": messages,
                "max_tokens": 4096
            }).encode()

            req = Request(
                "https://api.openai.com/v1/chat/completions",
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
            )

            with urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                
                # Extract reply from OpenAI response
                choices = result.get("choices", [])
                if not choices:
                    reply = ""
                else:
                    reply = choices[0].get("message", {}).get("content", "")
                
                # Return in documented format while maintaining backward compatibility
                response = {
                    "ok": True,
                    "cit": "v1",
                    "time": now_utc_iso(),
                    "model": result.get("model", OPENAI_MODEL),
                    "reply": reply,
                    "api": "openai",
                    "raw": result  # Keep raw response for backward compatibility
                }
                self.send_json(response)

        except URLError as e:
            self.send_json({"error": f"API помилка: {str(e)}"}, 500)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_settings(self, data):
        global OPENAI_API_KEY, OPENAI_MODEL
        
        if "apiKey" in data:
            OPENAI_API_KEY = data["apiKey"]
            save_config()
        if "model" in data:
            OPENAI_MODEL = data["model"]
            save_config()
        
        self.send_json({"status": "ok"})
    
    def handle_audit_report(self):
        """Обробник для /audit - повний звіт аудиту"""
        if not AUDIT_ENABLED:
            self.send_json({"error": "Audit module not available"}, 503)
            return
        
        try:
            audit = get_audit_instance()
            
            # Отримати параметри з query string
            hours = 24
            if "?" in self.path:
                try:
                    query = self.path.split("?")[1]
                    params = {}
                    for qc in query.split("&"):
                        if "=" in qc:
                            key, value = qc.split("=", 1)
                            params[key] = value
                    hours = int(params.get("hours", 24))
                except (ValueError, TypeError, AttributeError):
                    hours = 24  # Використати за замовчуванням при невірному значенні
            
            summary = audit.get_audit_summary(hours=hours)
            self.send_json(summary)
        except Exception as e:
            self.send_json({"error": f"Audit failed: {str(e)}"}, 500)
    
    def handle_audit_resources(self):
        """Обробник для /audit/resources - аудит ресурсів"""
        if not AUDIT_ENABLED:
            self.send_json({"error": "Audit module not available"}, 503)
            return
        
        try:
            audit = get_audit_instance()
            result = audit.audit_resources()
            self.send_json(result)
        except Exception as e:
            self.send_json({"error": f"Resource audit failed: {str(e)}"}, 500)

# ============ Config Management ============
def load_config():
    global OPENAI_API_KEY, OPENAI_MODEL
    config_file = DATA_DIR / "config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                OPENAI_API_KEY = config.get("api_key", OPENAI_API_KEY)
                OPENAI_MODEL = config.get("model", OPENAI_MODEL)
        except:
            pass

def save_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    config_file = DATA_DIR / "config.json"
    with open(config_file, "w") as f:
        json.dump({
            "api_key": OPENAI_API_KEY,
            "model": OPENAI_MODEL
        }, f)

# ============ Main ============
def open_browser():
    """Open browser after short delay"""
    import time
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}")

def main():
    load_config()
    
    print(f"""
╔═══════════════════════════════════════════╗
║                                           ║
║      🏠  Ci — Домашній асистент          ║
║                                           ║
║  Сервер запущено: http://localhost:{PORT}  ║
║                                           ║
║  Ctrl+C для зупинки                       ║
║                                           ║
╚═══════════════════════════════════════════╝
""")
    
    # Open browser in background
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server = HTTPServer((HOST, PORT), CiHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 До побачення!")
        server.shutdown()

if __name__ == "__main__":
    main()
