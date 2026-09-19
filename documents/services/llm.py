import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Ты — система извлечения данных из документов.
Из текста документа извлеки поля и верни СТРОГО валидный JSON без пояснений.

Поля:
- doc_number: номер документа (строка или null)
- doc_date: дата документа в формате YYYY-MM-DD (строка или null)
- counterparty: название контрагента (строка или null)
- amount: итоговая сумма числом (float или null)
- currency: валюта в формате ISO 4217 (RUB, USD, EUR) (строка или null)
- summary: краткое описание на русском, 1-2 предложения

Текст документа:
---
{text}
---

JSON:"""


def _call_openai(text: str) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": EXTRACTION_PROMPT.format(text=text[:8000])}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _call_ollama(text: str) -> dict:
    import requests

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": EXTRACTION_PROMPT.format(text=text[:8000]),
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )
    response.raise_for_status()
    raw = response.json().get("response", "{}")
    return json.loads(raw)


def extract_fields(text: str) -> dict:
    """Извлечь структурированные поля из текста документа."""
    if not text or len(text.strip()) < 20:
        return {"error": "Слишком короткий текст для анализа"}

    backend = getattr(settings, "LLM_BACKEND", "ollama")

    try:
        if backend == "openai":
            return _call_openai(text)
        return _call_ollama(text)
    except Exception as e:
        logger.exception("LLM extraction failed")
        return {"error": str(e)}
