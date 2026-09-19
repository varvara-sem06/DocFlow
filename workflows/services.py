import logging

from django.db import transaction
from django.utils import timezone

from documents.models import Document

from .models import ApprovalAction, ApprovalRequest
from .notifications import notify_approver, notify_owner_status_changed


class WorkflowError(Exception):
    """Ошибка бизнес-логики workflow."""


logger = logging.getLogger(__name__)


def _safe_notify(callback, *args, **kwargs):
    """Обёртка: уведомления не должны ломать основной поток."""
    try:
        callback(*args, **kwargs)
    except Exception:
        logger.exception("Уведомление не отправлено.")


@transaction.atomic
def start_approval(document: Document, route, user) -> ApprovalRequest:
    """Запустить согласование документа по маршруту."""
    if document.status in (Document.Status.ON_APPROVAL, Document.Status.APPROVED):
        raise WorkflowError("Документ уже на согласовании или согласован.")

    if not route.steps.exists():
        raise WorkflowError("В маршруте нет шагов.")

    request = ApprovalRequest.objects.create(
        document=document,
        route=route,
        started_by=user,
        current_step=route.steps.order_by("order").first().order,
    )

    ApprovalAction.objects.create(
        request=request,
        user=user,
        action=ApprovalAction.Action.SUBMIT,
        comment="Согласование запущено",
    )

    document.status = Document.Status.ON_APPROVAL
    document.save(update_fields=["status"])

    # Уведомление — после commit
    transaction.on_commit(lambda: _safe_notify(notify_approver, request))

    return request


@transaction.atomic
def approve_step(request: ApprovalRequest, user, comment: str = "") -> ApprovalRequest:
    """Согласовать текущий шаг и перейти к следующему."""
    if request.status != ApprovalRequest.Status.PENDING:
        raise WorkflowError("Согласование уже завершено.")

    current = request.route.steps.filter(order=request.current_step).first()
    if not current:
        raise WorkflowError("Текущий шаг не найден.")
    if current.approver_id != user.id:
        raise WorkflowError("Вы не являетесь согласующим на этом шаге.")

    ApprovalAction.objects.create(
        request=request,
        user=user,
        action=ApprovalAction.Action.APPROVE,
        comment=comment,
    )

    next_step = request.route.steps.filter(order__gt=request.current_step).first()

    if next_step:
        request.current_step = next_step.order
        request.save(update_fields=["current_step"])
        transaction.on_commit(lambda: _safe_notify(notify_approver, request))
    else:
        request.status = ApprovalRequest.Status.APPROVED
        request.finished_at = timezone.now()
        request.save(update_fields=["status", "finished_at"])

        request.document.status = Document.Status.APPROVED
        request.document.save(update_fields=["status"])

        transaction.on_commit(lambda: _safe_notify(notify_owner_status_changed, request))

    return request


@transaction.atomic
def reject_step(request: ApprovalRequest, user, comment: str = "") -> ApprovalRequest:
    """Отклонить согласование."""
    if request.status != ApprovalRequest.Status.PENDING:
        raise WorkflowError("Согласование уже завершено.")

    current = request.route.steps.filter(order=request.current_step).first()
    if not current or current.approver_id != user.id:
        raise WorkflowError("Вы не являетесь согласующим на этом шаге.")

    ApprovalAction.objects.create(
        request=request,
        user=user,
        action=ApprovalAction.Action.REJECT,
        comment=comment,
    )

    request.status = ApprovalRequest.Status.REJECTED
    request.finished_at = timezone.now()
    request.save(update_fields=["status", "finished_at"])

    request.document.status = Document.Status.REJECTED
    request.document.save(update_fields=["status"])

    transaction.on_commit(lambda: _safe_notify(notify_owner_status_changed, request))

    return request
