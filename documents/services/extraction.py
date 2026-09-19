"""Оркестратор: OCR → LLM → сохранение в документ."""

import logging

from documents.models import Document

from .llm import extract_fields
from .ocr import extract_text

logger = logging.getLogger(__name__)


def process_document(document_id: int) -> dict:
    """Полный пайплайн обработки документа."""
    document = Document.objects.get(id=document_id)

    if not document.file:
        logger.warning("У документа %s нет файла", document_id)
        return {"error": "Нет файла"}

    document.status = Document.Status.PROCESSING
    document.save(update_fields=["status"])

    try:
        file_path = document.file.path
        text = extract_text(file_path, document.mime_type)

        if not text:
            document.status = Document.Status.FAILED
            document.save(update_fields=["status"])
            return {"error": "Не удалось извлечь текст"}

        fields = extract_fields(text)

        document.extracted_data = {
            "raw_text": text[:5000],
            "fields": fields,
        }

        if fields.get("doc_number") and document.title in ("", "Без названия"):
            document.title = f"Документ №{fields['doc_number']}"

        document.status = Document.Status.UPLOADED
        document.save(update_fields=["extracted_data", "title", "status"])

        logger.info("Документ %s обработан", document_id)
        return fields

    except Exception as e:
        logger.exception("Ошибка обработки документа %s", document_id)
        document.status = Document.Status.FAILED
        document.save(update_fields=["status"])
        return {"error": str(e)}
