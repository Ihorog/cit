#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# === APPLY_API_ENGINE_NO_SWITCH.sh ===
# Автоматично визначає найкращий API (LOCAL → LAN → HF) і патчить UI.

API_LOCAL="http://127.0.0.1:8790"
API_LAN="http://192.168.1.145:8790"
API_HF="https://ihorog-cimeika-api.hf.space"

echo "=== [0] Перевірка UI директорій ==="
if [ -d "./ui" ]; then
  UI_DIR="./ui"
elif [ -d "./server/ui" ]; then
  UI_DIR="./server/ui"
else
  echo "⚠️ UI не знайдено (очікується ./ui або ./server/ui)"
  exit 1
fi

echo "=== [1] Оновлення API бази ==="
for f in $(find "$UI_DIR" -type f -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx"); do
  if grep -q "API_BASE" "$f"; then
    sed -i 's|API_BASE[^;]*;|let API_BASE="__AUTO__";|' "$f"
  fi
done

echo "=== [2] Перевірка доступності API ==="
if curl -s --max-time 1 "${API_LOCAL}/health" | grep -q "ok"; then
  API_SELECTED="$API_LOCAL"
elif curl -s --max-time 1 "${API_LAN}/health" | grep -q "ok"; then
  API_SELECTED="$API_LAN"
else
  API_SELECTED="$API_HF"
fi

echo "✅ Використовується API: $API_SELECTED"

echo "=== [3] Оновлення UI ==="
find "$UI_DIR" -type f -name "*.js" -o -name "*.ts" | xargs sed -i "s|__AUTO__|${API_SELECTED}|g"

echo "=== [4] Запуск локального UI :8010 ==="
pkill -f "http.server 8010" >/dev/null 2>&1 || true
nohup python -m http.server 8010 --directory "$UI_DIR" >/dev/null 2>&1 &

echo "=== [5] Перевірка ==="
sleep 0.5
echo -n "UI HEAD: "; curl -I -s "http://127.0.0.1:8010/" | head -n 1 || echo "FAIL"
echo -n "API health: "; curl -s "${API_SELECTED}/health" | head -c 100 || echo "FAIL"
echo
echo "=== READY ==="
echo "UI:  http://127.0.0.1:8010/"
echo "API: ${API_SELECTED}/health"
