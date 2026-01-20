import os
from PIL import Image # Потребує: pip install Pillow

def process_media():
    input_dir = "storage/uploads"
    output_base = "public/uk"
    
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        return "Створіть папку storage/uploads та покладіть туди фото."

    count = 0
    for file in os.listdir(input_dir):
        if file.endswith((".jpg", ".png", ".jpeg")):
            # Логіка сюжетної лінії: назва файлу визначає стан (напр. 'strength_01.jpg')
            parts = file.split('_')
            state = parts[0] if parts[0] in ['void', 'fatigue', 'strength', 'search', 'discovery', 'calm', 'storm'] else 'void'
            
            # Автоформатування: стискання для вебу
            img = Image.open(os.path.join(input_dir, file))
            img.thumbnail((1200, 1200)) # Оптимальний розмір
            
            # Комплектація в альбом
            for intent in os.listdir(os.path.join(output_base, state)):
                target_path = os.path.join(output_base, state, intent, "gallery")
                os.makedirs(target_path, exist_ok=True)
                img.save(os.path.join(target_path, file), "JPEG", quality=85)
                count += 1
                
    return f"Медіа-оркестрація завершена. Оновлено вузлів: {count}"

if __name__ == "__main__":
    print(process_media())
