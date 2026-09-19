import mimetypes

from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "original_filename"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Document.objects.filter(owner=self.request.user).select_related("owner")

        status = self.request.query_params.get("status")
        doc_type = self.request.query_params.get("doc_type")
        if status:
            qs = qs.filter(status=status)
        if doc_type:
            qs = qs.filter(doc_type=doc_type)

        return qs

    def perform_create(self, serializer):

        uploaded = self.request.FILES.get("file")
        extra = {"owner": self.request.user}

        if uploaded:
            extra["original_filename"] = uploaded.name
            extra["size_bytes"] = uploaded.size
            mime, _ = mimetypes.guess_type(uploaded.name)
            extra["mime_type"] = mime or uploaded.content_type or ""

        document = serializer.save(**extra)

        if document.file:
            from .tasks import process_document_task

            process_document_task.delay(document.id)
