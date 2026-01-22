#!/bin/bash

echo -e "\033[1;32m--- [Ciт] АВТОМАТИЗАЦІЯ РОЗГОРТАННЯ ВУЗЛА ---\033[0m"

# 1. Запит доступу до пам'яті (Критично для Android)
echo ">>> Налаштування сховища..."
termux-setup-storage
sleep 2

# 2. Оновлення репозиторіїв та пакетів (Тихий режим)
echo ">>> Оновлення системних компонентів..."
pkg update -y -o Dpkg::Options::="--force-confnew"
pkg upgrade -y -o Dpkg::Options::="--force-confnew"

# 3. Встановлення бази
echo ">>> Встановлення Python, Git, OpenSSH..."
pkg install python git openssh nano -y

# 4. Робота з файловою системою
cd $HOME
if [ -d "cit" ]; then
    echo ">>> Репозиторій знайдено. Оновлення..."
    cd cit
    git pull origin main
else
    echo ">>> Клонування ядра Ciт..."
    git clone https://github.com/Ihorog/cit.git
    cd cit
fi

# 5. Встановлення залежностей Python
echo ">>> Встановлення бібліотек Flask..."
pip install --upgrade pip
pip install flask flask_cors requests

# 6. Створення системного аліасу (Команда 'cit')
echo ">>> Створення команди швидкого запуску..."
if ! grep -q "alias cit=" $HOME/.bashrc; then
    echo 'alias cit="cd ~/cit && python server/cit_server.py"' >> $HOME/.bashrc
    echo "Аліас 'cit' додано в .bashrc"
fi

# 7. Генерація локального адмін-ключа (якщо немає)
if [ ! -f "storage/secure/device_identity.json" ]; then
    mkdir -p storage/secure
    echo ">>> Генерація паспорта вузла..."
    cat <<EOF > storage/secure/device_identity.json
{
    "role": "ADMIN",
    "node_type": "TERMUX_AUTO",
    "install_date": "$(date)",
    "permissions": "FULL"
}
EOF
fi

# 8. Фіналізація
echo -e "\033[1;32m--- [УСПІХ] ВУЗОЛ ГОТОВИЙ ---\033[0m"
echo "Перезапустіть Termux або введіть: source ~/.bashrc"
echo "Для запуску сервера просто введіть команду: cit"
