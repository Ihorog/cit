#!/bin/bash
cd /data/data/com.termux/files/home/cimeika/cit
pkill -f cit_server.py
echo "1. Введи свій API KEY (sk-proj-...):"
read -r K
sed -i '/OPENAI_API_KEY/d' .env
echo "OPENAI_API_KEY=$K" >> .env
export OPENAI_API_KEY=$K
echo "2. Запуск сервера..."
nohup python server/cit_server.py > logs/cit_server_stdout.log 2>&1 &
echo "3. Очікуємо 5 секунд для ініціалізації..."
sleep 5
echo "4. Тестовий запит:"
curl -s -X POST http://127.0.0.1:8794/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Test", "persona_id": "ci"}' | python -m json.tool
