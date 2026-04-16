import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.character_analyzer.agent import CharacterAnalyzerAgent

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Character Analyzer Agent", version="1.0.0")

# Инициализация агента (LLM-клиент будет передан через переменные окружения или заглушка)
# Здесь для примера используем заглушку, в реальности нужно подключить Qwen или др.
class MockLLM:
    def generate(self, prompt: str) -> str:
        import json
        return json.dumps({
            "role": "unknown",
            "archetype": "everyman",
            "traits": [],
            "description": "",
            "quote": ""
        })

# Замените на реальный клиент LLM при интеграции
llm = MockLLM()
agent = CharacterAnalyzerAgent(llm_model=llm, spacy_model="en_core_web_lg", min_mentions=5)

class AnalyzeRequest(BaseModel):
    full_text: str
    # можно добавить min_mentions, но пока оставим как в агенте

class AnalyzeResponse(BaseModel):
    characters: list
    relationships: list

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        logger.info(f"Received text of length {len(request.full_text)}")
        result = agent.process({"full_text": request.full_text})
        return result
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}