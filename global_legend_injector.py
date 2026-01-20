import os

theses = {
    "uk": {
        "create": "Ci-вузол створення: перетворення наміру на видимий елемент простору.",
        "observe": "Вузол спостереження: фіксація подій як частини спільного потоку.",
        "understand": "Вузол розуміння: Ci-інтерпретація, що узгоджує приватне зі спільним.",
        "share": "Поле обміну: простір, де сенси стають доступними для всіх учасників.",
        "protect": "Захисний контур: забезпечення цілісності та приватності простору Cimeika.",
        "fix": "Модуль корекції: відновлення узгодженості після виявлення розбіжностей.",
        "evolve": "Вектор еволюції: безперервний розвиток системи через накопичення досвіду."
    },
    "en": {
        "create": "Ci-node of creation: transforming intent into a visible spatial element.",
        "observe": "Observation node: recording events as part of a shared flow.",
        "understand": "Understanding node: Ci-interpretation that aligns private and shared fields.",
        "share": "Exchange field: a space where meanings become accessible to all participants.",
        "protect": "Protective contour: ensuring the integrity and privacy of the Cimeika space.",
        "fix": "Correction module: restoring alignment after detecting discrepancies.",
        "evolve": "Evolution vector: continuous system growth through experience accumulation."
    }
}

for lang in ["uk", "en"]:
    base_path = f"public/{lang}"
    if os.path.exists(base_path):
        count = 0
        for root, dirs, files in os.walk(base_path):
            for intent, line in theses[lang].items():
                if intent in root and "index.html" in files:
                    file_path = os.path.join(root, "index.html")
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write(f"\n<div class='ci-core-text' style='margin-top:20px; border-left:2px solid #00d4ff; padding-left:10px;'>")
                        f.write(f"<p><i>System {lang.upper()}:</i> {line}</p></div>")
                    count += 1
        print(f"Sector {lang.upper()} updated: {count} nodes.")
