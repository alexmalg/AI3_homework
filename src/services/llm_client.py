# ============================================================================
# llm_client.py - LLM API клиент для работы с MentorPiece API
# ============================================================================


import requests
import json
from typing import Optional
from src.config import Config


class LLMClient:
    """
    Класс для взаимодействия с LLM API (MentorPiece).
    """

    def __init__(self):
        self.api_endpoint = Config.API_ENDPOINT
        self.api_key = Config.API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.timeout = 30

    def call_llm(self, model_name: str, prompt: str) -> Optional[str]:
        """
        Главный метод для вызова LLM модели через API.
        
        РЕЖИМЫ РАБОТЫ:
        1. Обычный режим (ENABLE_MOCKS=False): реальные запросы к API
        2. Тестовый режим Cypress (ENABLE_MOCKS=True): мокированные ответы
        3. Pytest тесты: используют @mock.patch, не зависят от ENABLE_MOCKS
        """
        
        # ====================================================================
        # РЕЖИМ ТЕСТИРОВАНИЯ: Если включены мокированные ответы для Cypress
        # ====================================================================
        if Config.ENABLE_MOCKS:
            print(f"🔧 MOCK MODE (Cypress): Возврат мокированного ответа")
            
            # Мокированные ответы для разных моделей
            if "Qwen" in model_name:
                print(f"📚 Mock перевод для модели Qwen")
                return "The sun is shining."
            elif "claude-sonnet" in model_name:
                print(f"📚 Mock оценка для модели claude-sonnet")
                return "Rating: 9/10. Fluent and accurate."
            else:
                print(f"📚 Mock ответ для неизвестной модели")
                return "Mocked Response: Default answer"
        
        # ====================================================================
        # ОБЫЧНЫЙ РЕЖИМ: Реальный запрос к API
        # ====================================================================
        
        request_body = {
            "model_name": model_name,
            "prompt": prompt
        }
        
        try:
            print(f"📤 Отправка запроса к API...")
            print(f"   Модель: {model_name}")
            print(f"   Промпт: {prompt[:100]}...")
            
            response = requests.post(
                url=self.api_endpoint,
                json=request_body,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"   Текст ошибки: {response.text}")
                return None
            
            response_data = response.json()
            
            if "response" not in response_data:
                print(f"❌ Ошибка парсинга: ключ 'response' не найден в ответе")
                print(f"   Полученный ответ: {response_data}")
                return None
            
            llm_response = response_data["response"]
            
            print(f"✅ Успешный ответ от API ({len(llm_response)} символов)")
            
            return llm_response
        
        except requests.exceptions.Timeout:
            print(f"❌ Ошибка: Таймаут запроса (сервер не ответил за {self.timeout} сек)")
            return None
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Ошибка: Не удалось подключиться к API")
            print(f"   Проверьте интернет соединение и доступность {self.api_endpoint}")
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка HTTP запроса: {str(e)}")
            return None
        
        except json.JSONDecodeError:
            print(f"❌ Ошибка: Ответ сервера не является валидным JSON")
            print(f"   Полученный текст: {response.text[:200]}")
            return None
        
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {str(e)}")
            return None


client = LLMClient()

def call_llm(model_name: str, prompt: str) -> Optional[str]:
    """
    Функция-обертка для вызова LLM.
    """
    return client.call_llm(model_name, prompt)
