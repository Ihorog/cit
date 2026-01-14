#!/bin/bash
LOG_FILE="logs/cit_server_stdout.log"
echo "--- Останні 20 подій сервера CIT ---"
tail -n 20 "$LOG_FILE"
echo "------------------------------------"
echo "Бажаєте спостерігати в реальному часі? (y/n)"
read -t 5 answer
if [ "$answer" = "y" ]; then
    tail -f "$LOG_FILE"
fi
