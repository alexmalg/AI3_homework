# ============================================================================
# test_app.py - Юнит-тесты для Flask приложения "AI Translator & Critic"
# ============================================================================
# Этот файл содержит полный набор тестов для проверки логики приложения.
#
# Структура:
# 1. Тесты позитивных сценариев (success cases)
# 2. Тесты обработки ошибок (error handling)
# 3. Тесты валидации входных данных
# 4. Тесты загрузки переменных окружения
#
# Фреймворк: pytest с использованием unittest.mock для mocking API запросов
#
# Начинающим QA-специалистам: каждый тест проверяет определенный аспект
# приложения. Читайте комментарии для понимания логики тестирования.
# ============================================================================

import pytest
import os
from unittest import mock
from src.app import (
    app,
    validate_translation_input,
    build_translation_prompt,
    build_evaluation_prompt
)
from src.config import Config
from src.services.llm_client import call_llm


# ============================================================================
# ФИКСТУРЫ (FIXTURES)
# ============================================================================
# Фикстуры - это вспомогательные объекты, которые используются во всех тестах.
# Они инициализируются перед каждым тестом и удаляются после.
# Это помогает избежать дублирования кода.
# Начинающим QA-специалистам: фикстуры - это как "подготовка к тесту"

@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента Flask.
    
    Что происходит:
    1. Создаем Flask test client
    2. Отключаем проверку CSRF токенов (для тестирования)
    3. Используем test mode для лучшей обработки исключений
    
    Возвращает:
        FlaskClient: объект для отправки HTTP запросов в тестах
    
    Пример использования в тесте:
        def test_example(client):
            response = client.get('/')
            assert response.status_code == 200
    """
    
    # Отключаем проверку CSRF для тестирования
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    # Создаем тестовый клиент
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def mock_api_response_success():
    """
    Фикстура для мокирования успешного ответа от API.
    
    Что происходит:
    1. Создаем mock объект, который имитирует успешный HTTP ответ
    2. Устанавливаем status_code = 200 (OK)
    3. Настраиваем метод json() для возврата фиктивного текста
    
    Возвращает:
        Mock: объект, который имитирует requests.Response
    
    Пример структуры ответа API:
        {
            "response": "Привет, это переведенный текст"
        }
    """
    
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "This is a translated text"
    }
    return mock_response


@pytest.fixture
def mock_api_response_error():
    """
    Фикстура для мокирования ошибки API (500 Internal Server Error).
    
    Что происходит:
    1. Создаем mock объект, который имитирует ошибку сервера
    2. Устанавливаем status_code = 500
    3. Возвращаем текст ошибки
    
    Это симулирует ситуацию, когда сервер выбросил исключение.
    """
    
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    return mock_response


@pytest.fixture
def mock_api_response_invalid_json():
    """
    Фикстура для мокирования невалидного JSON ответа.
    
    Что происходит:
    1. Создаем mock объект с status_code = 200 (выглядит успешно)
    2. Но метод json() выбрасывает исключение JSONDecodeError
    
    Это симулирует ситуацию, когда сервер вернул неправильный JSON.
    """
    
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.text = "This is not valid JSON"
    mock_response.json.side_effect = ValueError("Invalid JSON")
    return mock_response


# ============================================================================
# ПОЗИТИВНЫЕ ТЕСТЫ (HAPPY PATH)
# ============================================================================
# Эти тесты проверяют, что приложение работает правильно в нормальных условиях
# Начинающим QA-специалистам: позитивные тесты проверяют успешные сценарии

class TestPositiveScenarios:
    """
    Группа тестов для проверки успешных сценариев работы приложения.
    """
    
    def test_homepage_loads_successfully(self, client):
        """
        Тест 1.1: Проверка загрузки главной страницы (GET /)
        
        Что проверяем:
        1. Что GET запрос на / возвращает статус код 200 (успешно)
        2. Что ответ содержит HTML с формой
        3. Что доступны все языки из конфигурации
        
        Ожидаемый результат:
        - Статус код: 200
        - Страница содержит текст "AI Translator & Critic"
        - Страница содержит текст "Перевести"
        """
        
        # Отправляем GET запрос на главную страницу
        response = client.get('/')
        
        # Проверяем статус код
        assert response.status_code == 200, \
            f"Ожидалось 200, получено {response.status_code}"
        
        # Проверяем, что ответ содержит HTML
        assert response.data is not None, "Ответ не содержит данных"
        
        # Проверяем, что в HTML есть заголовок приложения
        assert b'AI Translator & Critic' in response.data, \
            "Заголовок приложения не найден в HTML"
        
        # Проверяем, что форма содержит кнопку "Перевести"
        response_text = response.data.decode('utf-8')
        assert 'Перевести' in response_text or \
               'value="text"' in response_text, \
            "Кнопка 'Перевести' или форма не найдена"
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_successful_translation(self, mock_post, client, mock_api_response_success):
        """
        Тест 1.2: Проверка успешного перевода текста
        
        Что происходит:
        1. Мокируем функцию requests.post (HTTP запрос к API)
        2. Отправляем POST запрос на / с текстом и языком
        3. Проверяем, что API был вызван
        4. Проверяем, что в ответе есть переведенный текст
        
        Мокирование:
        - requests.post() теперь возвращает mock_api_response_success
        - API не будет вызван по-настоящему (экономим токены!)
        
        Ожидаемый результат:
        - Статус код: 200
        - Ответ содержит оригинальный текст
        - Ответ содержит переведенный текст
        """
        
        # Настраиваем mock для возврата успешного ответа
        mock_post.return_value = mock_api_response_success
        
        # Подготавливаем данные для отправки в форме
        form_data = {
            'text': 'Hello world',
            'language': 'english'
        }
        
        # Отправляем POST запрос
        response = client.post('/', data=form_data, follow_redirects=True)
        
        # Проверяем статус код
        assert response.status_code == 200, \
            f"Ожидалось 200, получено {response.status_code}"
        
        # Проверяем, что mock был вызван (значит, функция сработала)
        assert mock_post.called, "requests.post не был вызван"
        
        # Проверяем, что в ответе есть оригинальный текст
        assert b'Hello world' in response.data, \
            "Оригинальный текст не найден в ответе"
        
        # Проверяем, что API был вызван 2 раза (для перевода и оценки)
        assert mock_post.call_count == 2, \
            f"API должен быть вызван 2 раза (перевод + оценка), вызовов: {mock_post.call_count}"
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_translation_api_called_with_correct_parameters(
        self, mock_post, client, mock_api_response_success
    ):
        """
        Тест 1.3: Проверка корректности параметров при вызове API
        
        Что проверяем:
        1. Что API вызывается с правильным model_name
        2. Что API вызывается с правильным промптом
        3. Что API вызывается с правильными headers (Authorization)
        
        Это важно для убеждения, что мы отправляем правильные данные на сервер.
        """
        
        # Настраиваем mock
        mock_post.return_value = mock_api_response_success
        
        # Отправляем запрос
        form_data = {'text': 'Test text', 'language': 'english'}
        client.post('/', data=form_data)
        
        # Проверяем первый вызов API (для перевода)
        first_call = mock_post.call_args_list[0]
        
        # Проверяем URL API
        assert first_call[1]['url'] == Config.API_ENDPOINT, \
            f"Неправильный URL: {first_call[1]['url']}"
        
        # Проверяем, что в заголовках есть Authorization
        headers = first_call[1]['headers']
        assert 'Authorization' in headers, \
            "Authorization header не найден"
        assert headers['Authorization'].startswith('Bearer '), \
            "Authorization header имеет неправильный формат"


# ============================================================================
# ТЕСТЫ ОБРАБОТКИ ОШИБОК
# ============================================================================
# Эти тесты проверяют, что приложение корректно обрабатывает ошибки
# Начинающим QA-специалистам: тесты ошибок очень важны! Они гарантируют,
# что приложение не сломается в случае проблем

class TestErrorHandling:
    """
    Группа тестов для проверки обработки ошибок.
    """
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_api_server_error_handled_gracefully(
        self, mock_post, client, mock_api_response_error
    ):
        """
        Тест 2.1: Проверка обработки ошибки сервера (500)
        
        Что происходит:
        1. Мокируем функцию requests.post для возврата ошибки 500
        2. Отправляем POST запрос на перевод
        3. Проверяем, что приложение не падает
        4. Проверяем, что пользователю показана ошибка
        
        Ожидаемый результат:
        - Статус код ответа: 200 (приложение не сломалось)
        - В HTML есть текст об ошибке
        """
        
        # Настраиваем mock для возврата ошибки сервера
        mock_post.return_value = mock_api_response_error
        
        # Отправляем запрос
        form_data = {'text': 'Test text', 'language': 'english'}
        response = client.post('/', data=form_data)
        
        # Проверяем, что приложение вернуло статус 200 (не сломалось)
        assert response.status_code == 200, \
            f"Приложение упало с ошибкой {response.status_code}"
        
        # Проверяем, что в ответе есть сообщение об ошибке
        # (может быть на русском или английском)
        response_text = response.data.decode('utf-8')
        assert 'ошибка' in response_text.lower() or 'error' in response_text.lower(), \
            "Сообщение об ошибке не найдено в ответе"
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_connection_error_handled(self, mock_post, client):
        """
        Тест 2.2: Проверка обработки ошибки соединения
        
        Что происходит:
        1. Мокируем requests.post для выбрасывания исключения ConnectionError
        2. Отправляем POST запрос
        3. Проверяем, что приложение не упало
        4. Проверяем, что показана ошибка
        
        Это симулирует ситуацию, когда интернет недоступен.
        """
        
        # Настраиваем mock для выбрасывания ошибки соединения
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Failed to establish connection"
        )
        
        # Отправляем запрос
        form_data = {'text': 'Test text', 'language': 'english'}
        response = client.post('/', data=form_data)
        
        # Проверяем, что приложение не упало
        assert response.status_code == 200
        
        # Проверяем, что в ответе есть указание на ошибку
        response_text = response.data.decode('utf-8')
        assert 'ошибка' in response_text.lower() or 'error' in response_text.lower()
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_timeout_error_handled(self, mock_post, client):
        """
        Тест 2.3: Проверка обработки ошибки таймаута
        
        Что происходит:
        1. Мокируем requests.post для выбрасывания исключения Timeout
        2. Отправляем POST запрос
        3. Проверяем, что приложение справилось с ошибкой
        
        Это симулирует ситуацию, когда сервер отвечает очень долго.
        """
        
        # Настраиваем mock для выбрасывания ошибки таймаута
        import requests
        mock_post.side_effect = requests.exceptions.Timeout(
            "Request timed out"
        )
        
        # Отправляем запрос
        form_data = {'text': 'Test text', 'language': 'english'}
        response = client.post('/', data=form_data)
        
        # Проверяем результат
        assert response.status_code == 200
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_invalid_json_response_handled(
        self, mock_post, client, mock_api_response_invalid_json
    ):
        """
        Тест 2.4: Проверка обработки невалидного JSON от API
        
        Что происходит:
        1. API возвращает невалидный JSON
        2. call_llm должен обработать это без ошибок
        3. Приложение должно показать ошибку пользователю
        
        Это проверяет, что обработка JSON ошибок работает корректно.
        """
        
        # Настраиваем mock для возврата невалидного JSON
        mock_post.return_value = mock_api_response_invalid_json
        
        # Отправляем запрос
        form_data = {'text': 'Test text', 'language': 'english'}
        response = client.post('/', data=form_data)
        
        # Проверяем, что приложение справилось
        assert response.status_code == 200


# ============================================================================
# ТЕСТЫ ВАЛИДАЦИИ ВХОДНЫХ ДАННЫХ
# ============================================================================
# Эти тесты проверяют функцию validate_translation_input
# Начинающим QA-специалистам: валидация очень важна для безопасности

class TestInputValidation:
    """
    Группа тестов для проверки валидации входных данных.
    """
    
    def test_empty_text_validation(self):
        """
        Тест 3.1: Проверка что пустой текст отклоняется
        
        Ожидаемый результат:
        - is_valid = False
        - error_message содержит информацию об ошибке
        """
        
        # Тестируем с пустым текстом
        result = validate_translation_input("", "english")
        
        # Проверяем результат
        assert result['is_valid'] is False, \
            "Пустой текст не должен быть валидным"
        assert result['error_message'] is not None, \
            "Должно быть сообщение об ошибке"
    
    def test_whitespace_only_text_validation(self):
        """
        Тест 3.2: Проверка что текст только с пробелами отклоняется
        
        Это важно, потому что "   " выглядит как текст, но это просто пробелы
        """
        
        result = validate_translation_input("   ", "english")
        assert result['is_valid'] is False
    
    def test_text_exceeds_max_length(self):
        """
        Тест 3.3: Проверка что очень длинный текст отклоняется
        
        Для защиты от DDoS атак и перегрузки сервера,
        мы ограничиваем максимальную длину текста
        """
        
        # Создаем текст длиннее максимально разрешенной
        long_text = "a" * (Config.MAX_TEXT_LENGTH + 1)
        
        result = validate_translation_input(long_text, "english")
        
        # Проверяем результат
        assert result['is_valid'] is False
        assert 'длинн' in result['error_message'].lower(), \
            "Сообщение об ошибке должно упоминать длину текста"
    
    def test_unsupported_language_validation(self):
        """
        Тест 3.4: Проверка что неподдерживаемый язык отклоняется
        
        Мы не можем переводить на языки, которые не в Config.SUPPORTED_LANGUAGES
        """
        
        result = validate_translation_input("Test text", "klingon")
        
        assert result['is_valid'] is False
        assert 'язык' in result['error_message'].lower() or \
               'language' in result['error_message'].lower()
    
    def test_valid_input_passes_validation(self):
        """
        Тест 3.5: Проверка что корректный ввод проходит валидацию
        
        Это "позитивный" сценарий для валидации
        """
        
        result = validate_translation_input(
            "This is a test text",
            "english"
        )
        
        # Проверяем результат
        assert result['is_valid'] is True, \
            "Корректный ввод должен быть валидным"
        assert result['error_message'] is None


# ============================================================================
# ТЕСТЫ ПОСТРОЕНИЯ ПРОМПТОВ
# ============================================================================
# Эти тесты проверяют, что промпты формируются правильно
# Начинающим QA-специалистам: правильные промпты => качественные ответы

class TestPromptBuilding:
    """
    Группа тестов для проверки построения промптов.
    """
    
    def test_translation_prompt_contains_text(self):
        """
        Тест 4.1: Проверка что промпт для перевода содержит исходный текст
        
        Если текст не будет в промпте, LLM не сможет его переводить!
        """
        
        text = "Hello world"
        prompt = build_translation_prompt(text, "english")
        
        # Проверяем, что промпт содержит исходный текст
        assert text in prompt, \
            f"Промпт должен содержать исходный текст '{text}'"
        
        # Проверяем, что промпт содержит инструкцию на английском
        assert 'translate' in prompt.lower() or 'перевед' in prompt.lower(), \
            "Промпт должен содержать инструкцию для перевода"
    
    def test_translation_prompt_contains_language(self):
        """
        Тест 4.2: Проверка что промпт содержит целевой язык
        
        LLM должен знать, на какой язык переводить!
        """
        
        prompt = build_translation_prompt("Text", "french")
        
        # Проверяем, что промпт содержит название языка
        assert 'french' in prompt.lower(), \
            "Промпт должен содержать название целевого языка"
    
    def test_evaluation_prompt_contains_both_texts(self):
        """
        Тест 4.3: Проверка что промпт для оценки содержит оба текста
        
        LLM-as-a-Judge должен видеть оригинал и перевод для сравнения!
        """
        
        original = "Original text"
        translated = "Переведенный текст"
        
        prompt = build_evaluation_prompt(original, translated)
        
        # Проверяем, что оба текста в промпте
        assert original in prompt, \
            "Промпт должен содержать оригинальный текст"
        assert translated in prompt, \
            "Промпт должен содержать переведенный текст"
        
        # Проверяем, что есть инструкция для оценки
        assert 'evaluat' in prompt.lower() or 'оцен' in prompt.lower(), \
            "Промпт должен содержать инструкцию для оценки"


# ============================================================================
# ТЕСТЫ ЗАГРУЗКИ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================================================
# Эти тесты проверяют, что API ключ правильно загружается из .env
# Начинающим QA-специалистам: тесты окружения очень важны!

class TestEnvironmentVariables:
    """
    Группа тестов для проверки загрузки переменных окружения.
    """
    
    def test_api_key_loaded_from_environment(self):
        """
        Тест 5.1: Проверка что API ключ загружается из os.getenv
        
        Config должен загружать API_KEY из переменной окружения MENTORPIECE_API_KEY
        """
        
        # Проверяем, что Config.API_KEY установлен
        assert Config.API_KEY is not None, \
            "API_KEY не установлен в Config"
        
        # Проверяем, что это не значение по умолчанию "your-api-key-here"
        # (это значение используется только в примере .env файла)
        # В реальности это может быть любой ключ
        assert isinstance(Config.API_KEY, str), \
            "API_KEY должна быть строкой"
    
    def test_api_endpoint_configured(self):
        """
        Тест 5.2: Проверка что API endpoint правильно установлен
        
        Config.API_ENDPOINT должна быть правильным URL
        """
        
        # Проверяем, что endpoint установлен
        assert Config.API_ENDPOINT is not None
        
        # Проверяем, что это URL (начинается с http)
        assert Config.API_ENDPOINT.startswith('http'), \
            "API_ENDPOINT должен быть URL"
    
    def test_supported_languages_configured(self):
        """
        Тест 5.3: Проверка что поддерживаемые языки загружены
        
        Config.SUPPORTED_LANGUAGES должен быть непустым словарем
        """
        
        # Проверяем, что словарь не пустой
        assert len(Config.SUPPORTED_LANGUAGES) > 0, \
            "SUPPORTED_LANGUAGES не должен быть пустым"
        
        # Проверяем, что это словарь
        assert isinstance(Config.SUPPORTED_LANGUAGES, dict), \
            "SUPPORTED_LANGUAGES должен быть словарем"


# ============================================================================
# ТЕСТЫ ФУНКЦИИ call_llm
# ============================================================================
# Эти тесты проверяют функцию call_llm из llm_client.py
# Начинающим QA-специалистам: это главная функция, которая работает с API

class TestCallLLM:
    """
    Группа тестов для функции call_llm.
    """
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_call_llm_returns_response_text(
        self, mock_post, mock_api_response_success
    ):
        """
        Тест 6.1: Проверка что call_llm возвращает текст ответа
        
        Когда API возвращает успешный ответ, call_llm должен вернуть text поле.
        """
        
        # Настраиваем mock
        mock_post.return_value = mock_api_response_success
        
        # Вызываем функцию
        result = call_llm("test_model", "test_prompt")
        
        # Проверяем результат
        assert result is not None, \
            "call_llm должна вернуть текст при успешном ответе"
        assert isinstance(result, str), \
            "call_llm должна вернуть строку"
        assert result == "This is a translated text"
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_call_llm_returns_none_on_api_error(
        self, mock_post, mock_api_response_error
    ):
        """
        Тест 6.2: Проверка что call_llm возвращает None при ошибке API
        
        Когда API возвращает ошибку (status_code >= 400),
        call_llm должна вернуть None вместо того, чтобы упасть.
        """
        
        # Настраиваем mock для ошибки
        mock_post.return_value = mock_api_response_error
        
        # Вызываем функцию
        result = call_llm("test_model", "test_prompt")
        
        # Проверяем результат
        assert result is None, \
            "call_llm должна вернуть None при ошибке API"
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_call_llm_handles_missing_response_key(self, mock_post):
        """
        Тест 6.3: Проверка что call_llm обрабатывает отсутствие ключа 'response'
        
        Если API вернет JSON без ключа 'response', call_llm должна вернуть None.
        """
        
        # Настраиваем mock для возврата JSON без нужного ключа
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"wrong_key": "value"}
        mock_post.return_value = mock_response
        
        # Вызываем функцию
        result = call_llm("test_model", "test_prompt")
        
        # Проверяем результат
        assert result is None, \
            "call_llm должна вернуть None если ключа 'response' нет"


# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================
# Эти тесты проверяют работу нескольких компонентов вместе
# Начинающим QA-специалистам: интеграционные тесты очень важны!

class TestIntegration:
    """
    Группа интеграционных тестов.
    """
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_full_workflow_with_both_api_calls(
        self, mock_post, client, mock_api_response_success
    ):
        """
        Тест 7.1: Проверка полного workflow: перевод + оценка
        
        Что происходит:
        1. Пользователь отправляет текст на перевод
        2. Приложение вызывает API для перевода
        3. Приложение вызывает API для оценки перевода
        4. Приложение возвращает результаты пользователю
        
        Это самый важный тест, который проверяет весь процесс!
        """
        
        # Настраиваем mock для возврата разных ответов
        # Первый вызов (перевод) вернет один ответ
        # Второй вызов (оценка) вернет другой ответ
        mock_response_1 = mock.Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "response": "Translated text"
        }
        
        mock_response_2 = mock.Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "response": "Rating: 9/10"
        }
        
        # Настраиваем mock для возврата разных ответов при разных вызовах
        mock_post.side_effect = [mock_response_1, mock_response_2]
        
        # Отправляем запрос
        form_data = {
            'text': 'Original English text',
            'language': 'english'
        }
        response = client.post('/', data=form_data)
        
        # Проверяем результаты
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        
        # Проверяем, что оба API вызова произошли
        assert mock_post.call_count == 2, \
            f"Должно быть 2 вызова API (перевод + оценка), было {mock_post.call_count}"
        
        # Проверяем, что результаты доступны в ответе
        assert 'Original English text' in response_text or 'English' in response_text
    
    @mock.patch('src.services.llm_client.requests.post')
    def test_workflow_with_first_api_call_failure(
        self, mock_post, client, mock_api_response_error
    ):
        """
        Тест 7.2: Проверка workflow когда первый API вызов (перевод) падает
        
        Что происходит:
        1. Пользователь отправляет текст
        2. API для перевода возвращает ошибку
        3. Приложение должно показать ошибку и не вызывать оценку
        
        Это важно, чтобы не тратить ресурсы на оценку если перевода нет.
        """
        
        # Настраиваем mock для возврата ошибки
        mock_post.return_value = mock_api_response_error
        
        # Отправляем запрос
        form_data = {
            'text': 'Test text',
            'language': 'english'
        }
        response = client.post('/', data=form_data)
        
        # Проверяем, что приложение справилось
        assert response.status_code == 200
        
        # Проверяем, что API был вызван только 1 раз (перевод)
        # Оценка не должна быть вызвана если перевод упал
        assert mock_post.call_count <= 2, \
            "API должен быть вызван максимум 2 раза"


# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================
# Для запуска тестов используйте команду:
#     pytest tests/unit/test_app.py -v
#
# Для запуска конкретного теста:
#     pytest tests/unit/test_app.py::TestPositiveScenarios::test_homepage_loads_successfully -v
#
# Для запуска тестов с покрытием:
#     pytest tests/unit/test_app.py --cov=src --cov-report=html
