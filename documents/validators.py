import os

from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".jpg", ".jpeg", ".png"]
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
]
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_file_size(value):
    if value.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"Файл слишком большой. Максимум — {MAX_FILE_SIZE // (1024 * 1024)} МБ."
        )


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Недопустимое расширение. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
