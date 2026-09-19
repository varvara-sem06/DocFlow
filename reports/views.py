from django.http import FileResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document

from .exporters import export_documents_to_excel
from .services.analytics import (
    dashboard_stats,
    documents_timeline,
    top_counterparties,
    users_activity,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):
    return Response(dashboard_stats(request.user))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def timeline(request):
    days = int(request.query_params.get("days", 30))
    return Response({"days": days, "data": documents_timeline(days, request.user)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_counterparties_view(request):
    limit = int(request.query_params.get("limit", 10))
    return Response({"data": top_counterparties(limit, request.user)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def users_activity_view(request):
    return Response({"data": users_activity()})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def export_documents(request):
    qs = Document.objects.all()
    if not request.user.is_staff:
        qs = qs.filter(owner=request.user)

    buffer = export_documents_to_excel(qs)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename="documents.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
