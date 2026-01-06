#!/usr/bin/env python3
with open('server/cit_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Знайти рядок 518: if self.path == "/ui" or self.path == "/ui/":
insert_idx = None
for i, line in enumerate(lines):
    if 'if self.path == "/ui" or self.path == "/ui/":' in line:
        insert_idx = i
        break

if insert_idx is None:
    print("❌ Не знайдено /ui route")
    exit(1)

print(f"✅ Знайдено /ui на рядку {insert_idx + 1}")

# PWA routes (з правильним відступом — 8 пробілів)
pwa_code = '''        # === PWA ROUTES ===
        if self.path == "/manifest.webmanifest":
            try:
                import os
                manifest_path = os.path.join(os.path.dirname(__file__), "..", "ui", "manifest.webmanifest")
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    body = mf.read().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/manifest+json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Manifest not found: {e}".encode())
                return

        if self.path.startswith("/icons/"):
            try:
                import os
                filename = self.path.split("/icons/")[1]
                icon_path = os.path.join(os.path.dirname(__file__), "..", "ui", "icons", filename)
                with open(icon_path, "rb") as icf:
                    body = icf.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Icon not found: {e}".encode())
                return

'''

# Вставити ПЕРЕД if self.path == "/ui"
lines.insert(insert_idx, pwa_code)

# Видалити Flask routes з кінця (після if __name__)
cleaned_lines = []
skip_flask = False
for line in lines:
    if 'if __name__ == "__main__":' in line:
        skip_flask = False  # Зберігаємо if __name__
    if '@app.route' in line or 'def manifest():' in line or 'def icon(f):' in line:
        skip_flask = True
        continue
    if skip_flask and (line.strip().startswith('def ') or line.strip() == ''):
        skip_flask = False
    if not skip_flask:
        cleaned_lines.append(line)

# Записати
with open('server/cit_server.py', 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print("✅ PWA routes додано в HTTPServer")
print("✅ Flask routes видалено")
