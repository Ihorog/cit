import os

theses = [
    "Магія існує там, де ми її помічаємо.",
    "Сила системи в її здатності оберігати приватність родини.",
    "Кожен рядок коду — це цеглина нашої цифрової фортеці.",
    "Ми дихаємо разом із природою: від Молодика до Повні.",
    "Проєкт Сі — це казка, написана мовою програмування."
]

base_path = "public/uk"

if os.path.exists(base_path):
    count = 0
    # Наповнюємо всі папки в public/uk
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == "index.html":
                file_path = os.path.join(root, file)
                # Випадкова теза для різноманітності
                import random
                thesis = random.choice(theses)
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n<footer style='margin-top:50px; opacity:0.6; font-size:0.8em;'>")
                    f.write(f"<hr><p><b>Теза системи:</b> {thesis}</p></footer>")
                count += 1
    print(f"Інтегровано тези у {count} вузлів.")
