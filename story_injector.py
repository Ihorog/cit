import os

stories = {
    "void": "Ми починаємо з нуля. Порожнеча — це полотно для нашої магії.",
    "strength": "Кожен рядок коду — це цеглина нашої фортеці.",
    "search": "Марійка каже, що магія ховається у деталях. Ми шукаємо її разом."
}

base_path = "public/uk"

if not os.path.exists(base_path):
    print(f"Помилка: Шлях {base_path} не знайдено!")
else:
    count = 0
    for state, text in stories.items():
        state_dir = os.path.join(base_path, state)
        if os.path.exists(state_dir):
            for intent in os.listdir(state_dir):
                file_path = os.path.join(state_dir, intent, "index.html")
                if os.path.isfile(file_path):
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write(f"\n<div class='story-box' style='margin-top:20px; border-left:4px solid #00d4ff; padding-left:10px;'>")
                        f.write(f"<p><i>Голос Казкаря:</i> {text}</p></div>")
                    count += 1
    print(f"Успішно оновлено {count} вузлів сюжетними текстами.")
