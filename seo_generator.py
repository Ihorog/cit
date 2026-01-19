import os
import yaml
# Оновлена назва файлу
matrix_file = 'cimeika_matrix.yaml'
if not os.path.exists(matrix_file):
    print(f"ERROR: File {matrix_file} NOT FOUND in {os.getcwd()}")
    # Виведемо список файлів для діагностики
    print("Files in directory:", os.listdir('.'))
    exit()
with open(matrix_file, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
langs = ['en', 'uk']
states = data.get('states', [])
intents = data.get('intents', [])
base_path = "public"
count = 0
for lang in langs:
    for state in states:
        for intent in intents:
            dir_path = os.path.join(base_path, lang, state, intent)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, "index.html"), "w", encoding="utf-8") as html:
                html.write(f"<h1>{state.capitalize()} - {intent.capitalize()} ({lang})</h1>")
            count += 1
print(f"SUCCESS: Generated {count} SEO-nodes in {base_path}/")
