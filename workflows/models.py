from django.conf import settings
from django.db import models

from documents.models import Document


class ApprovalRoute(models.Model):
    """Маршрут согласования - шаблон, который можно применять к документам."""

    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    doc_type = models.CharField(
        "Тип документа",
        max_length=20,
        choices=Document.DocType.choices,
        blank=True,
        help_text="Если пусто — маршрут универсальный",
    )
    is_active = models.BooleanField("Активен", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_routes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Маршрут согласования"
        verbose_name_plural = "Маршруты согласования"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ApprovalStep(models.Model):
    """Шаг маршрута — кто и в каком порядке согласует."""

    route = models.ForeignKey(
        ApprovalRoute,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    order = models.PositiveIntegerField("Порядок", default=1)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_steps",
    )
    is_required = models.BooleanField("Обязателен", default=True)

    class Meta:
        verbose_name = "Шаг маршрута"
        verbose_name_plural = "Шаги маршрута"
        ordering = ["route", "order"]
        unique_together = [("route", "order")]

    def __str__(self):
        return f"{self.route.name} — шаг {self.order}: {self.approver.username}"


class ApprovalRequest(models.Model):
    """Запущенный процесс согласования конкретного документа."""

    class Status(models.TextChoices):
        PENDING = "pending", "В процессе"
        APPROVED = "approved", "Согласован"
        REJECTED = "rejected", "Отклонён"
        CANCELLED = "cancelled", "Отменён"

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="approval_requests",
    )
    route = models.ForeignKey(
        ApprovalRoute,
        on_delete=models.PROTECT,
        related_name="requests",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    current_step = models.PositiveIntegerField("Текущий шаг", default=1)
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="started_requests",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Запрос на согласование"
        verbose_name_plural = "Запросы на согласование"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Согласование #{self.id} — {self.document.title}"


class ApprovalAction(models.Model):
    """История действий — кто, когда, что сделал."""

    class Action(models.TextChoices):
        SUBMIT = "submit", "Отправлено"
        APPROVE = "approve", "Согласовано"
        REJECT = "reject", "Отклонено"
        COMMENT = "comment", "Комментарий"

    request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="approval_actions",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Действие"
        verbose_name_plural = "Действия"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.get_action_display()}"
