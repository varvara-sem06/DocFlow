from django.conf import settings
from django.db import models

from .validators import validate_file_extension, validate_file_size


class Document(models.Model):
    """Документ, загруженный пользователем для согласования."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        UPLOADED = "uploaded", "Загружен"
        PROCESSING = "processing", "В обработке"
        ON_APPROVAL = "on_approval", "На согласовании"
        APPROVED = "approved", "Согласован"
        REJECTED = "rejected", "Отклонён"
        FAILED = "failed", "Ошибка обработки"

    class DocType(models.TextChoices):
        INVOICE = "invoice", "Счёт"
        CONTRACT = "contract", "Контракт"
        ACT = "act", "Акт"
        REPORT = "report", "Отчёт"
        OTHER = "other", "Другое"

    title = models.CharField("Название", max_length=255)
    doc_type = models.CharField(
        "Тип документа",
        max_length=20,
        choices=DocType.choices,
        default=DocType.OTHER,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    file = models.FileField(
        "Файл",
        upload_to="documents/%Y/%m",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_file_extension],
    )
    original_filename = models.CharField(
        "Исходное имя файла",
        max_length=255,
        blank=True,
        null=True,
    )
    mime_type = models.CharField(
        "MIME-тип",
        max_length=100,
        blank=True,
    )
    size_bytes = models.PositiveBigIntegerField(
        "Размер (байт)",
        default=0,
    )

    extracted_data = models.JSONField(
        "Извлечённые данные",
        default=dict,
        blank=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField("Создан", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлён", auto_now=True)

    class Meta:
        verbose_name = ("Документ",)
        verbose_name_plural = ("Документы",)
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["doc_type"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
