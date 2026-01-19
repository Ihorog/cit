# scripts/bot_keyboard.py
from telebot import types

def get_upload_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # Кнопки вибору сюжетної лінії
    btn_search = types.InlineKeyboardButton("🔍 Пошук Магії", callback_data="upload_search")
    btn_strength = types.InlineKeyboardButton("🛡️ Сила Родини", callback_data="upload_strength")
    btn_discovery = types.InlineKeyboardButton("✨ Відкриття", callback_data="upload_discovery")
    
    markup.add(btn_search, btn_strength, btn_discovery)
    return markup