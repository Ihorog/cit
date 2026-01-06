#!/data/data/com.termux/files/usr/bin/bash
ROOT="$HOME/cimeika/cit"
cd "$ROOT" || exit 1
echo "🚀 [CIT SYNC] Перевіряю стан репозиторію..."
git pull --rebase origin main || true
git add -A
git commit -m "🤖 AutoSync local commit" || echo "Немає змін"
git push origin main || echo "Push пропущено"
echo "✅ [CIT SYNC] Готово."
