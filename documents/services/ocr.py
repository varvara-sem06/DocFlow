import logging

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_pdf(path: str) -> str:
    """Пробуем сначала текстовый слой PDF, потом OCR."""
    text_parts = []

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
    except Exception as e:
        logger.warning("pdfplumber не смог прочитать %s: %s", path, e)

    text = "\n".join(text_parts).strip()

    if len(text) < 50:
        logger.info("PDF %s без текстового слоя, запускаем OCR", path)
        try:
            images = convert_from_path(path, dpi=200)
            ocr_parts = [pytesseract.image_to_string(img, lang="rus+eng") for img in images]
            text = "\n".join(ocr_parts).strip()
        except Exception as e:
            logger.error("OCR PDF упал: %s", e)

    return text


def extract_text_from_image(path: str) -> str:
    """OCR для картинок."""
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img, lang="rus+eng").strip()
    except Exception as e:
        logger.error("OCR image упал: %s", e)
        return ""


def extract_text(path: str, mime_type: str = "") -> str:
    """Универсальная точка входа."""
    path_lower = path.lower()

    if path_lower.endswith(".pdf") or "pdf" in mime_type:
        return extract_text_from_pdf(path)
    if path_lower.endswith((".jpg", ".jpeg", ".png")) or "image" in mime_type:
        return extract_text_from_image(path)

    return ""
