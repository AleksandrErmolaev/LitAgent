import json
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LLMClient:
    """Обёртка над реальной LLM (например, llama.cpp)."""
    def __init__(self, model):
        # model — объект с методом generate(prompt) -> str
        self.model = model

    def generate(self, prompt: str) -> str:
        if self.model is None:
            raise RuntimeError("LLM не инициализирована")
        return self.model.generate(prompt)

    def parse_character_response(self, response: str, name: str) -> Optional[Dict[str, Any]]:
        """Извлекает JSON из ответа LLM."""
        try:
            # Ищем JSON внутри ```json ... ``` или просто фигурные скобки
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                start = response.find('{')
                end = response.rfind('}')
                if start != -1 and end != -1:
                    json_str = response[start:end+1]
                else:
                    raise ValueError("JSON не найден")

            data = json.loads(json_str)
            # Проверка обязательных полей
            required = ["role", "archetype", "traits", "description", "quote"]
            for field in required:
                if field not in data:
                    logger.warning(f"Поле '{field}' отсутствует в ответе для {name}")
                    data[field] = "" if field != "traits" else []
            return data
        except Exception as e:
            logger.error(f"Ошибка парсинга ответа LLM для {name}: {e}")
            return None