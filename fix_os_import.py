with open('server/cit_server.py', 'r') as f:
    lines = f.readlines()

# Знайти def do_GET(self):
for i, line in enumerate(lines):
    if 'def do_GET(self):' in line:
        # Перевірити чи вже є import os
        if i + 1 < len(lines) and 'import os' not in lines[i + 1]:
            # Додати import os одразу після def do_GET
            lines.insert(i + 1, '        import os\n')
            print(f"✅ Додано 'import os' на початку do_GET (рядок {i + 2})")
            break
        else:
            print("✅ import os вже є")
            break

# Видалити всі локальні import os всередині routes
cleaned = []
skip_next = False
for i, line in enumerate(lines):
    # Пропустити import os всередині if блоків (не на початку методу)
    if skip_next and 'import os' in line and line.strip() == 'import os':
        skip_next = False
        continue
    
    # Якщо це PWA route або /health route
    if 'if self.path ==' in line or 'if self.path.startswith' in line:
        skip_next = True
    
    # Якщо import os не на початку методу (має більший відступ)
    if 'import os' in line and line.startswith('            '):
        continue
    
    cleaned.append(line)

with open('server/cit_server.py', 'w') as f:
    f.writelines(cleaned)

print("✅ Локальні import os видалено")
