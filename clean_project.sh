#!/bin/bash

# ============================================================================
# clean_project.sh - Безопасная очистка проекта AI Translator & Critic
# ============================================================================
#
# Этот скрипт удаляет все временные, лишние и ненужные файлы,
# оставляя только необходимое для работы:
# - Flask приложение
# - Unit тесты
# - Cypress UI тесты
# - Документацию
#
# Использование: bash clean_project.sh
#
# ============================================================================

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║         🧹 ОЧИСТКА ПРОЕКТА - AI Translator & Critic                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Счетчики
total_files=0
deleted_files=0
deleted_dirs=0

# ============================================================================
# ФАЗА 1: СКАНИРОВАНИЕ И ВЫВОД ЧТО БУДЕТ УДАЛЕНО
# ============================================================================

echo -e "${BLUE}📊 ФАЗА 1: АНАЛИЗ ФАЙЛОВ${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Файлы и папки для УДАЛЕНИЯ:${NC}"
echo ""

# Временные файлы Python
echo -e "${YELLOW}1️⃣  Python .pyc, .pyo, __pycache__:${NC}"
find . -type d -name "__pycache__" -not -path "./.git/*" -print | head -20
find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" \) -not -path "./.git/*" -print | wc -l | xargs echo "   Найдено .pyc/.pyo файлов:"
echo ""

# Pytest кэш
echo -e "${YELLOW}2️⃣  Pytest кэш (.pytest_cache):${NC}"
find . -type d -name ".pytest_cache" -not -path "./.git/*" -print
echo ""

# Cypress скриншоты и видео
echo -e "${YELLOW}3️⃣  Cypress скриншоты и видео:${NC}"
find . -path "*/cypress/screenshots" -o -path "*/cypress/videos" | grep -v ".git" | head -10
echo ""

# Логи
echo -e "${YELLOW}4️⃣  Логи и временные файлы:${NC}"
find . -type f \( -name "*.log" -o -name "nohup.out" -o -name ".DS_Store" \) -not -path "./.git/*" -print
echo ""

# Dockerfile'ы
echo -e "${YELLOW}5️⃣  Dockerfile'ы:${NC}"
find . -maxdepth 1 -type f -name "Dockerfile*" -print
echo ""

# Старая документация (используем только AQA_README.txt)
echo -e "${YELLOW}6️⃣  Старые файлы документации (оставляем AQA_README.txt):${NC}"
find . -maxdepth 1 -type f \( \
    -name "CYPRESS_INSTRUCTIONS.md" \
    -o -name "CYPRESS_QUICK_START.md" \
    -o -name "INSTALLATION_GUIDE.md" \
    -o -name "PROJECT_CREATED.txt" \
    -o -name "QA_DOCUMENTATION.md" \
    -o -name "README_PROJECT.md" \
    -o -name "UI_TESTS_SUMMARY.md" \
\) -print
echo ""

# Старые скрипты
echo -e "${YELLOW}7️⃣  Скрипты (оставляем run.py и run_cypress_tests.sh):${NC}"
find . -maxdepth 1 -type f \( \
    -name "setup.sh" \
    -o -name "QUICK_START.py" \
    -o -name "consolidate_qa_docs.py" \
\) -print
echo ""

# Node modules (нужны для Cypress, но список очень большой)
echo -e "${YELLOW}8️⃣  node_modules (ВНИМАНИЕ - нужны для Cypress):${NC}"
if [ -d "node_modules" ]; then
    du -sh node_modules
    echo "   ⚠️  node_modules НЕ БУДУТ УДАЛЕНЫ (нужны для Cypress!)"
fi
echo ""

# Остальное: test-results, venv_test, .git, etc
echo -e "${YELLOW}9️⃣  test-results папка:${NC}"
find . -maxdepth 1 -type d -name "test-results" -print
echo ""

echo ""
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# ФАЗА 2: ЗАПРОС ПОДТВЕРЖДЕНИЯ
# ============================================================================

echo -e "${BLUE}⚠️  ФАЗА 2: ПОДТВЕРЖДЕНИЕ${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}БУДУТ УДАЛЕНЫ:${NC}"
echo "  ✓ __pycache__ папки и *.pyc файлы"
echo "  ✓ .pytest_cache папка"
echo "  ✓ cypress/screenshots и cypress/videos"
echo "  ✓ *.log и nohup.out файлы"
echo "  ✓ Dockerfile и Dockerfile.* файлы"
echo "  ✓ Старые документационные файлы (кроме AQA_README.txt)"
echo "  ✓ Старые скрипты (setup.sh, QUICK_START.py, consolidate_qa_docs.py)"
echo "  ✓ test-results папка"
echo "  ✓ Пустые папки"
echo ""
echo -e "${GREEN}БУДУТ СОХРАНЕНЫ:${NC}"
echo "  ✓ src/ - Flask приложение"
echo "  ✓ tests/ - Unit тесты"
echo "  ✓ cypress/ - Cypress UI тесты"
echo "  ✓ venv_test/ - Python виртуальное окружение"
echo "  ✓ node_modules/ - Node зависимости для Cypress"
echo "  ✓ .env - Конфигурация окружения"
echo "  ✓ requirements.txt - Python зависимости"
echo "  ✓ package.json, package-lock.json - Node конфигурация"
echo "  ✓ cypress.config.js - Конфигурация Cypress"
echo "  ✓ run.py - Entry point Flask приложения"
echo "  ✓ run_cypress_tests.sh - Скрипт запуска тестов"
echo "  ✓ AQA_README.txt - Полная документация"
echo "  ✓ README.md - Главный README"
echo "  ✓ .git, .gitignore - Git конфигурация"
echo ""

read -p "Продолжить очистку? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Операция отменена."
    exit 1
fi

echo ""
echo -e "${BLUE}🔧 ФАЗА 3: УДАЛЕНИЕ ФАЙЛОВ${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# ФАЗА 3: УДАЛЕНИЕ ФАЙЛОВ
# ============================================================================

# 1. Удалить __pycache__ директории
echo -e "${YELLOW}[1/9]${NC} Удаляю __pycache__ папки..."
find . -type d -name "__pycache__" -not -path "./.git/*" | while read dir; do
    rm -rf "$dir"
    ((deleted_dirs++))
done
echo "✅ Готово"
echo ""

# 2. Удалить .pyc файлы
echo -e "${YELLOW}[2/9]${NC} Удаляю .pyc файлы..."
find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" \) -not -path "./.git/*" -delete
echo "✅ Готово"
echo ""

# 3. Удалить .pytest_cache
echo -e "${YELLOW}[3/9]${NC} Удаляю .pytest_cache..."
rm -rf .pytest_cache
echo "✅ Готово"
echo ""

# 4. Удалить Cypress скриншоты и видео
echo -e "${YELLOW}[4/9]${NC} Удаляю Cypress скриншоты и видео..."
rm -rf cypress/screenshots cypress/videos
echo "✅ Готово"
echo ""

# 5. Удалить логи
echo -e "${YELLOW}[5/9]${NC} Удаляю логи..."
find . -maxdepth 1 -type f \( -name "*.log" -o -name "nohup.out" \) -delete
find . -type f -name ".DS_Store" -delete
echo "✅ Готово"
echo ""

# 6. Удалить Dockerfile'ы
echo -e "${YELLOW}[6/9]${NC} Удаляю Dockerfile'ы..."
rm -f Dockerfile Dockerfile.cypress
echo "✅ Готово"
echo ""

# 7. Удалить старые документационные файлы
echo -e "${YELLOW}[7/9]${NC} Удаляю старые документационные файлы..."
rm -f CYPRESS_INSTRUCTIONS.md \
      CYPRESS_QUICK_START.md \
      INSTALLATION_GUIDE.md \
      PROJECT_CREATED.txt \
      QA_DOCUMENTATION.md \
      README_PROJECT.md \
      UI_TESTS_SUMMARY.md
echo "✅ Готово"
echo ""

# 8. Удалить старые скрипты
echo -e "${YELLOW}[8/9]${NC} Удаляю старые скрипты..."
rm -f setup.sh \
      QUICK_START.py \
      consolidate_qa_docs.py
echo "✅ Готово"
echo ""

# 9. Удалить test-results папку
echo -e "${YELLOW}[9/9]${NC} Удаляю test-results папку..."
rm -rf test-results
echo "✅ Готово"
echo ""

# ============================================================================
# ФАЗА 4: УДАЛЕНИЕ ПУСТЫХ ПАПОК
# ============================================================================

echo -e "${BLUE}🗑️  ФАЗА 4: УДАЛЕНИЕ ПУСТЫХ ПАПОК${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Ищу пустые папки...${NC}"
find . -type d -empty -not -path "./.git/*" -not -path "./node_modules/*" | while read dir; do
    rmdir "$dir" 2>/dev/null && {
        echo "  🗑️  $dir"
        ((deleted_dirs++))
    }
done
echo "✅ Готово"
echo ""

# ============================================================================
# ФАЗА 5: ПРОВЕРКА ЦЕЛОСТНОСТИ
# ============================================================================

echo -e "${BLUE}✅ ФАЗА 5: ПРОВЕРКА ЦЕЛОСТНОСТИ${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Проверяю что ВСЕ необходимые файлы остались:${NC}"
echo ""

files_ok=true

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗ ОТСУТСТВУЕТ${NC} $1"
        files_ok=false
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗ ОТСУТСТВУЕТ${NC} $1/"
        files_ok=false
    fi
}

echo "Flask приложение:"
check_dir "src"
check_file "run.py"
check_file "requirements.txt"
check_file ".env"
echo ""

echo "Unit тесты:"
check_dir "tests"
echo ""

echo "Cypress UI тесты:"
check_dir "cypress"
check_file "cypress.config.js"
check_file "package.json"
check_file "package-lock.json"
echo ""

echo "Документация:"
check_file "AQA_README.txt"
check_file "README.md"
echo ""

echo "Скрипты:"
check_file "run_cypress_tests.sh"
check_file "clean_project.sh"
echo ""

echo "Окружение:"
check_dir ".git"
check_dir "venv_test"
check_dir "node_modules"
echo ""

if [ "$files_ok" = true ]; then
    echo -e "${GREEN}✅ ВСЕ необходимые файлы присутствуют!${NC}"
else
    echo -e "${RED}❌ ВНИМАНИЕ: Некоторые файлы отсутствуют!${NC}"
fi

echo ""

# ============================================================================
# ФАЗА 6: ИТОГОВАЯ СТАТИСТИКА
# ============================================================================

echo -e "${BLUE}📊 ФАЗА 6: ИТОГОВАЯ СТАТИСТИКА${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# Размер проекта до и после
project_size=$(du -sh . | cut -f1)

echo -e "${GREEN}✅ ОЧИСТКА ЗАВЕРШЕНА!${NC}"
echo ""
echo "Статистика:"
echo "  📊 Текущий размер проекта: $project_size"
echo ""

# Структура проекта
echo "Структура проекта:"
echo ""
tree -L 2 -I 'node_modules|venv_test' --charset ascii 2>/dev/null || {
    find . -maxdepth 2 -not -path "*/node_modules/*" -not -path "*/venv_test/*" -not -path "./.git/*" | sort | sed 's|^\./||' | head -50
}
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# ФАЗА 7: ИНСТРУКЦИИ ПО ЗАПУСКУ
# ============================================================================

echo -e "${BLUE}🚀 ФАЗА 7: ИНСТРУКЦИИ ПО ЗАПУСКУ${NC}"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}Для запуска приложения:${NC}"
echo ""
echo "  Терминал 1 (Flask):"
echo "    cd /workspaces/AI3_homework"
echo "    ENABLE_MOCKS=true python run.py"
echo ""
echo "  Терминал 2 (Unit тесты):"
echo "    cd /workspaces/AI3_homework"
echo "    python -m pytest tests/unit/test_app.py -v"
echo ""
echo "  Терминал 3 (Cypress UI тесты):"
echo "    cd /workspaces/AI3_homework"
echo "    ENABLE_MOCKS=true npm run cypress:run"
echo ""
echo "  Или используя скрипт:"
echo "    bash run_cypress_tests.sh"
echo ""

echo "════════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ ПРОЕКТ ОЧИЩЕН И ГОТОВ!                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
