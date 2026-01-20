import os

system_theses = {
    "create": "Ci-вузол створення: перетворення наміру на видимий елемент простору.",
    "observe": "Вузол спостереження: фіксація подій як частини спільного потоку.",
    "understand": "Вузол розуміння: Ci-інтерпретація, що узгоджує приватне зі спільним.",
    "share": "Поле обміну: простір, де сенси стають доступними для всіх учасників.",
    "protect": "Захисний контур: забезпечення цілісності та приватності простору Cimeika.",
    "fix": "Модуль корекції: відновлення узгодженості після виявлення розбіжностей.",
    "evolve": "Вектор еволюції: безперервний розвиток системи через накопичення досвіду."
}

base_path = "public/uk"

if os.path.exists(base_path):
    count = 0
    for root, dirs, files in os.walk(base_path):
        for intent, line in system_theses.items():
            if intent in root and "index.html" in files:
                file_path = os.path.join(root, "index.html")
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n<div class='ci-core-text' style='margin-top:20px; border-left:2px solid #00d4ff; padding-left:10px;'>")
                    f.write(f"<p><i>Core System:</i> {line}</p></div>")
                count += 1
    print(f"Системні тези інтегровано: {count} вузлів оновлено.")
else:
    print("Помилка: Шлях public/uk не знайдено.")
