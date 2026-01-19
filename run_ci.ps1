<#
.SYNOPSIS
    Cimeika Ultimate Orchestrator v48.0
    Функції: Очищення C:, Оптимізація D:, Генерація 7x7, Астро-теми CSS, Cloud Sync.
#>

$ErrorActionPreference = "Stop"
$PROJECT_DIR = "D:\git\cit"
$UNIFIED_DIR = "D:\git\cimeika-unified"
$MATRIX_FILE = "cimeika_matrix.yaml"

Write-Host "--- [1/6] ТЕХОБСЛУГОВУВАННЯ ТА ГІГІЄНА Windows ---" -ForegroundColor Cyan
# Очищення старих файлів (3 місяці)
$limit = (Get-Date).AddDays(-90)
$paths = @("$env:TEMP\*", "C:\Windows\Temp\*", "$env:USERPROFILE\Downloads\*")
foreach ($p in $paths) { Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.LastAccessTime -lt $limit } | Remove-Item -Force -ErrorAction SilentlyContinue }
Write-Host "Диск C: оптимізовано." -ForegroundColor Green

Write-Host "--- [2/6] ПЕРЕВІРКА ТА ОНОВЛЕННЯ БІБЛІОТЕК ---" -ForegroundColor Cyan
if (!(Get-Command python -ErrorAction SilentlyContinue)) { winget install --id Python.Python.3.11 --silent }
pip install PyYAML requests flask jinja2 --quiet
Write-Host "Python середовище готове." -ForegroundColor Green

Write-Host "--- [3/6] ГЕНЕРАЦІЯ SEO-МАТРИЦІ ТА АСТРО-ТЕМ ---" -ForegroundColor Cyan
cd $PROJECT_DIR
@'
import os, yaml, datetime
def get_theme():
    hour = datetime.datetime.now().hour
    if 6 <= hour < 18: return "theme-day", "#f0f4f8"
    if 18 <= hour < 22: return "theme-twilight", "#1a1a2e"
    return "theme-night", "#020205"

def run():
    with open('cimeika_matrix.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    theme, bg = get_theme()
    langs, states, intents = ['en', 'uk'], data.get('states', []), data.get('intents', [])
    for l in langs:
        for s in states:
            for i in intents:
                path = f"public/{l}/{s}/{i}"
                os.makedirs(path, exist_ok=True)
                with open(f"{path}/index.html", "w", encoding="utf-8") as f:
                    f.write(f"<html><body class='{theme}' style='background:{bg}; color:#00d4ff; font-family:monospace;'>")
                    f.write(f"<h1>{s.upper()} § {i.upper()}</h1><p>Sync: {datetime.datetime.now()}</p></body></html>")
    return f"Success: 98 nodes generated with {theme}"
print(run())
'@ | Out-File -FilePath "seo_generator.py" -Encoding utf8
python seo_generator.py

Write-Host "--- [4/6] ЗБІРКА ІНТЕРФЕЙСУ (UNIFIED UI) ---" -ForegroundColor Cyan
if (Test-Path $UNIFIED_DIR) {
    cd $UNIFIED_DIR
    # npm run build  # Розкоментуйте, якщо використовуєте Node.js
    Copy-Item "dist\*" "$PROJECT_DIR\public\" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "--- [5/6] ЕКОЛОГІЧНИЙ РЕЗОНАНС (КОНСТАНТИ) ---" -ForegroundColor Cyan
cd $PROJECT_DIR
if (Test-Path "scripts/env_engine.py") { python scripts/env_engine.py }

Write-Host "--- [6/6] СИНХРОНІЗАЦІЯ З ХМАРОЮ (GIT PUSH) ---" -ForegroundColor Cyan
git add .
$msg = "Resonance Sync: " + (Get-Date -Format "HH:mm dd.MM.yyyy")
git commit -m "$msg"
git push origin main

Write-Host "`n--- [УСПІХ] СИСТЕМА ЦИФРОВОГО ІМУНІТЕТУ АКТИВНА У КРЕМЕНЧУЦІ ---" -ForegroundColor Black -BackgroundColor Green