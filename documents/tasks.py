from celery import shared_task

from .services.extraction import process_document


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_document_task(self, document_id: int):
    """Обработать документ в фоне: OCR + LLM."""
    try:
        return process_document(document_id)
    except Exception as exc:
        raise self.retry(exc=exc) from exc
