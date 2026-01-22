#!/bin/bash
# CIMEIKA RECOVERY MASTER SCRIPT (GEC-5)
# Призначення: Повне відновлення структури вузла з GitHub

echo -e "\033[1;35m--- [Ciт] ЗАПУСК ПРОТОКОЛУ ВІДНОВЛЕННЯ (GEC-5) ---\033[0m"

# 1. Перевірка середовища
cd $HOME
if [ ! -d "cit" ]; then
    echo ">>> Репозиторій не знайдено. Клонування..."
    git clone https://github.com/Ihorog/cit.git
fi
cd cit

# 2. Примусова синхронізація з Реєстром Істини
echo ">>> Синхронізація з GitHub (origin/main)..."
git fetch --all
git reset --hard origin/main

# 3. Валідація через Ci Guard
echo ">>> Перевірка цілісності вузла..."
python core/gec_core.py --check

if [ $? -eq 0 ]; then
    echo -e "\033[1;32m[SUCCESS] Систему відновлено до канонічного стану.\033[0m"
    # Оновлення аліасів
    source ~/.bashrc
    echo "Запуск системи..."
    cit
else
    echo -e "\033[1;31m[CRITICAL] Помилка валідації. Перевірте matrix.json та паспорти.\033[0m"
    exit 1
fi
