import os

# Словник сенсів для Галереї
gallery_texts = {
    "void": "Цифрова Порожнеча: Місце, де кожен піксель чекає на свою історію.",
    "fatigue": "Архіви Втоми: Фотографії, що вчать нас цінувати тихий відпочинок.",
    "strength": "Скарбниця Сили: Моменти, коли ми відчували себе непереможними.",
    "search": "Мапа Пошуку: Тут зберігаються сліди магії, яку ми шукаємо з Марійкою.",
    "discovery": "Зала Відкриттів: Візуальні свідчення того, як світ відкривається нам.",
    "calm": "Оаза Спокою: Артефакти домашнього тепла та Маминої посмішки.",
    "storm": "Хроніка Шторму: Енергія наших мрій у динамічних образах."
}

base_path = "public/uk"

if os.path.exists(base_path):
    count = 0
    for state in gallery_texts:
        state_dir = os.path.join(base_path, state)
        if os.path.exists(state_dir):
            for intent in os.listdir(state_dir):
                file_path = os.path.join(state_dir, intent, "index.html")
                if os.path.isfile(file_path):
                    content = gallery_texts[state]
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write(f"\n<section class='gallery-meta' style='border:1px dashed #112244; padding:15px; margin-top:30px;'>")
                        f.write(f"<h3>🖼️ Галерея§Календар: {state.capitalize()}</h3>")
                        f.write(f"<p>{content}</p></section>")
                    count += 1
    print(f"Галерея текстувана: {count} вузлів активовано.")
