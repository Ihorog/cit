#!/data/data/com.termux/files/usr/bin/bash
ROOT="$HOME/cimeika/cit"
cd "$ROOT" || exit 1
echo "🚀 [CIT SYNC] Перевірка стану репозиторію..."
git pull --rebase origin main || true
git add -A
git commit -m "🤖 AutoSync commit (автоматично)" || echo "Без змін"
git push origin main || echo "Push пропущено"
python "$HOME/cimeika/cit/ci_report.py"
echo "✅ [CIT SYNC] Завершено."
