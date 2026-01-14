#!/bin/bash

# Скрипт для тестування Vercel deployment локально

set -e

echo "🔍 Перевірка наявності Vercel CLI..."
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI не встановлено. Встановлюємо..."
    npm install -g vercel@latest
fi

echo "✅ Vercel CLI знайдено"

echo ""
echo "📦 Встановлення залежностей..."
cd web
npm install

echo ""
echo "🏗️  Збірка проекту..."
npm run build

echo ""
echo "✅ Збірка успішна!"

echo ""
echo "🚀 Готово до деплою на Vercel"
echo ""
echo "Для деплою виконайте:"
echo "  vercel --prod"
echo ""
echo "Або використайте GitHub Actions для автоматичного деплою при push"
