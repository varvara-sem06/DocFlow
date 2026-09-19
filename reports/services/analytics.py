from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from documents.models import Document
from workflows.models import ApprovalAction, ApprovalRequest


def dashboard_stats(user=None):
    """Общая статистика для дашборда."""
    docs = Document.objects.all()
    requests = ApprovalRequest.objects.all()

    if user and not user.is_staff:
        docs = docs.filter(owner=user)
        requests = requests.filter(document__owner=user)

    total_docs = docs.count()
    by_status = dict(docs.values_list("status").annotate(c=Count("id")).values_list("status", "c"))
    by_type = dict(
        docs.values_list("doc_type").annotate(c=Count("id")).values_list("doc_type", "c")
    )

    approved = requests.filter(
        status=ApprovalRequest.Status.APPROVED,
        finished_at__isnull=False,
    )
    avg_duration = None
    durations = [(r.finished_at - r.started_at).total_seconds() / 3600 for r in approved]
    if durations:
        avg_duration = round(sum(durations) / len(durations), 2)

    total_amount = 0
    for doc in docs.filter(status=Document.Status.APPROVED):
        amount = (doc.extracted_data or {}).get("fields", {}).get("amount")
        if isinstance(amount, (int, float)):
            total_amount += amount

    return {
        "total_documents": total_docs,
        "by_status": by_status,
        "by_type": by_type,
        "total_approval_requests": requests.count(),
        "pending_requests": requests.filter(status=ApprovalRequest.Status.PENDING).count(),
        "approved_requests": requests.filter(status=ApprovalRequest.Status.APPROVED).count(),
        "rejected_requests": requests.filter(status=ApprovalRequest.Status.REJECTED).count(),
        "avg_approval_hours": avg_duration,
        "total_approved_amount": round(total_amount, 2),
    }


def documents_timeline(days: int = 30, user=None):
    """Динамика загрузки документов по дням."""
    since = timezone.now() - timedelta(days=days)
    qs = Document.objects.filter(created_at__gte=since)

    if user and not user.is_staff:
        qs = qs.filter(owner=user)

    rows = (
        qs.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    return [{"date": r["day"].isoformat(), "count": r["count"]} for r in rows]


def top_counterparties(limit: int = 10, user=None):
    """Топ контрагентов по количеству документов."""
    qs = Document.objects.filter(status=Document.Status.APPROVED)

    if user and not user.is_staff:
        qs = qs.filter(owner=user)

    counter = {}
    for doc in qs:
        fields = (doc.extracted_data or {}).get("fields", {})
        cp = fields.get("counterparty")
        if cp:
            counter[cp] = counter.get(cp, 0) + 1

    sorted_items = sorted(counter.items(), key=lambda x: -x[1])[:limit]
    return [{"counterparty": k, "count": v} for k, v in sorted_items]


def users_activity(limit: int = 10):
    """Активность пользователей по действиям согласования."""
    rows = (
        ApprovalAction.objects.values("user__username")
        .annotate(total=Count("id"))
        .order_by("-total")[:limit]
    )
    return [{"username": r["user__username"], "actions": r["total"]} for r in rows]
