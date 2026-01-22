import os

def get_actions_by_ext(file_name):
    ext = file_name.split('.')[-1].lower()
    
    # Словник стандартних дій за форматами
    logic = {
        'img': ['Зберегти в Галерею', 'Зробити аватаром', 'Обробити (AI)'],
        'vid': ['Додати в Кінотеку', 'Зберегти як Short', 'Монтаж'],
        'aud': ['В Аудіотеку', 'Перетворити в текст', 'Фоновий звук'],
        'doc': ['В Канони Ci', 'Додати в Wiki', 'Архів']
    }

    if ext in ['jpg', 'png', 'webp']: category = 'img'
    elif ext in ['mp4', 'mkv', 'mov']: category = 'vid'
    elif ext in ['mp3', 'wav', 'ogg']: category = 'aud'
    else: category = 'doc'

    return logic.get(category, ['Зберегти', 'Архів', 'Тимчасово'])

# Після вибору дії система очікує текстовий коментар користувача
