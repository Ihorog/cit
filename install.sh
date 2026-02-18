#!/bin/bash
# CIMEIKA INSTALL — Автоматичне розгортання системного агента Ci
# Перевіряє та встановлює залежності, налаштовує конфігурацію aichat.
# Призначений для середовища Termux (Android).

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

CI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AICHAT_CONFIG_DIR="$HOME/.config/aichat"
ROLE_DIR="$AICHAT_CONFIG_DIR/roles"

log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "${RED}✗${NC} $1"; }

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  CIMEIKA — Встановлення агента Ci      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# --- Визначення пакетного менеджера ---
install_pkg() {
    if command -v pkg &> /dev/null; then
        pkg install -y "$@"
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y "$@"
    elif command -v brew &> /dev/null; then
        brew install "$@"
    else
        log_err "Не знайдено пакетний менеджер (pkg/apt-get/brew)."
        return 1
    fi
}

# --- 1. Перевірка залежностей ---
echo -e "${CYAN}[1/4] Перевірка залежностей${NC}"

DEPS_OK=true

for dep in git curl fzf; do
    if command -v "$dep" &> /dev/null; then
        log_ok "$dep: встановлений"
    else
        log_warn "$dep: не знайдений — встановлюю..."
        install_pkg "$dep" || { log_err "Не вдалося встановити $dep"; DEPS_OK=false; }
    fi
done

# aichat — потребує окремої установки
if command -v aichat &> /dev/null; then
    log_ok "aichat: встановлений"
else
    log_warn "aichat: не знайдений — встановлюю..."
    if command -v cargo &> /dev/null; then
        cargo install aichat || { log_err "Не вдалося встановити aichat через cargo"; DEPS_OK=false; }
    elif command -v pkg &> /dev/null; then
        pkg install -y aichat 2>/dev/null || {
            log_warn "aichat недоступний через pkg, спроба через cargo..."
            pkg install -y rust 2>/dev/null || true
            cargo install aichat 2>/dev/null || { log_err "Не вдалося встановити aichat"; DEPS_OK=false; }
        }
    else
        log_err "Встановіть aichat вручну: https://github.com/sigoden/aichat"
        DEPS_OK=false
    fi
fi

if [ "$DEPS_OK" = false ]; then
    log_warn "Деякі залежності не встановлені. Продовжую налаштування..."
fi

# --- 2. Конфігурація aichat ---
echo ""
echo -e "${CYAN}[2/4] Налаштування конфігурації aichat${NC}"

mkdir -p "$AICHAT_CONFIG_DIR" "$ROLE_DIR"

if [ ! -f "$AICHAT_CONFIG_DIR/config.yaml" ]; then
    cp "$CI_ROOT/config/aichat.yaml" "$AICHAT_CONFIG_DIR/config.yaml"
    log_ok "config.yaml створений: $AICHAT_CONFIG_DIR/config.yaml"
else
    log_ok "config.yaml вже існує"
fi

# --- 3. Встановлення ролі cimeika ---
echo ""
echo -e "${CYAN}[3/4] Встановлення ролі Оркестратора${NC}"

cp "$CI_ROOT/config/roles/cimeika.md" "$ROLE_DIR/cimeika.md"
log_ok "Роль cimeika встановлена: $ROLE_DIR/cimeika.md"

# --- 4. Встановлення виконуваного файлу ci ---
echo ""
echo -e "${CYAN}[4/4] Налаштування команди ci${NC}"

chmod +x "$CI_ROOT/bin/ci"

# Додати bin/ до PATH якщо ще не додано
CI_BIN="$CI_ROOT/bin"
PROFILE_FILE="$HOME/.bashrc"
if [ -f "$HOME/.bash_profile" ]; then
    PROFILE_FILE="$HOME/.bash_profile"
fi

if ! echo "$PATH" | grep -q "$CI_BIN"; then
    echo "export PATH=\"$CI_BIN:\$PATH\"" >> "$PROFILE_FILE"
    log_ok "PATH оновлено у $PROFILE_FILE"
    export PATH="$CI_BIN:$PATH"
else
    log_ok "bin/ci вже у PATH"
fi

log_ok "Команда ci готова до використання"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Встановлення завершено              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Використання:"
echo "  ci chat    — Діалог з Оркестратором"
echo "  ci status  — Перевірка системи"
echo "  ci sync    — Синхронізація змін"
echo ""
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo -e "${YELLOW}⚠ Встановіть API ключ:${NC}"
    echo "  export OPENAI_API_KEY=\"sk-...\""
    echo ""
fi
