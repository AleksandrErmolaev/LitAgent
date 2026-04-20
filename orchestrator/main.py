from fastapi import FastAPI, HTTPException
import requests
import time

app = FastAPI(title="Orchestrator")

BOOKER_URL = "http://booker:8000/fetch_full"
SUMMARIZER_URL = "http://summarizer:8000/summarize"
QUESTIONS_URL = "http://questiongenerator:8000/generate"
CHARACTER_URL = "http://character:8000/analyze"


@app.post("/analyze")
def analyze(request: dict):
    start_time = time.time()

    try:
        # 1. Booker
        book = requests.post(BOOKER_URL, json=request).json()

        if book.get("status") == "error":
            raise HTTPException(status_code=404, detail=book)

        text = book.get("text", "")
        chapters = book.get("chapters", [])

        # 🔥 ограничение для скорости (ВАЖНО)
        chapters = chapters[:5]
        short_text = " ".join(chapters)

        # 2. Summarizer
        summary = requests.post(
            SUMMARIZER_URL,
            json={"text": short_text, "chapters": chapters}
        ).json()

        # 3. Questions
        questions = requests.post(
            QUESTIONS_URL,
            json={"text": short_text, "chapters": chapters}
        ).json()

        # 4. Characters
        characters = requests.post(
            CHARACTER_URL,
            json={"full_text": short_text}
        ).json()

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "metadata": {
                "title": book.get("title"),
                "author": book.get("author"),
                "language": book.get("language"),
                "word_count": book.get("word_count"),
                "processing_time_ms": processing_time
            },
            "summary": summary,
            "questions": questions,
            "characters": characters
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))