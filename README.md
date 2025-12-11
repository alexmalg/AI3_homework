AI Translator & Critic

Веб-приложение на Flask для перевода текста и оценки качества перевода с помощью LLM через MentorPiece API.

Обзор проекта

Основные компоненты:
- Backend: Flask-приложение (src/app.py), конфигурация (src/config.py), LLM-клиент (src/services/llm_client.py)
- Frontend: HTML-шаблон с формой ввода и отображением результата (src/templates/index.html)
- Автотесты: unit-тесты на pytest (tests/unit/) и UI-тесты на Cypress (cypress/e2e/). Подробная документация в AQA_README.txt

Структура репозитория

src/
  app.py                      - Flask-приложение, маршруты, обработка форм
  config.py                   - Конфигурация приложения (включая флаг ENABLE_MOCKS)
  services/
    llm_client.py            - Клиент для LLM / MentorPiece API (с поддержкой моков)
  templates/
    index.html               - Основная страница UI

tests/
  unit/
    test_app.py              - 23 unit-теста (pytest)
  conftest.py                - Фикстуры для pytest

cypress/
  e2e/
    translator_critic.cy.js  - 4 UI-теста (Cypress)
  screenshots/               - Скриншоты упавших тестов
  support/                   - Вспомогательные файлы Cypress

AQA_README.txt               - Детальная документация по автотестам
requirements.txt             - Python-зависимости
pytest.ini                   - Конфигурация pytest
package.json                 - JS-зависимости и NPM-скрипты (Cypress)
cypress.config.js            - Конфигурация Cypress
.env                         - Переменные окружения (API ключ)

Установка и окружение

Требования:
- Python 3.12+ (проверьте: python --version)
- Node.js 18+ и npm (проверьте: node --version, npm --version)

Установка:

cd /workspaces/AI3_homework

Опционально создать и активировать виртуальное окружение:
python -m venv venv
source venv/bin/activate    (Linux/macOS)
или:
venv\Scripts\Activate.ps1   (Windows PowerShell)

Установить Python-зависимости:
pip install -r requirements.txt

Установить JS-зависимости (Cypress и др.):
npm install

Создать файл .env с API-ключом:
echo "MENTORPIECE_API_KEY=your-api-key-here" > .env

Запуск приложения

Обычный запуск (с реальными запросами к API):

python -m src.app

Откройте браузер: http://localhost:5000

Детали:
Подробная документация по запуску и тестированию находится в файле AQA_README.txt.
