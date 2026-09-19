from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор документа - превращает модель в JSON и обратно"""

    owner_username = serializers.CharField(source="owner.username", read_only=True)

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "doc_type",
            "doc_type_display",
            "status",
            "status_display",
            "file",
            "original_filename",
            "mime_type",
            "size_bytes",
            "extracted_data",
            "owner",
            "owner_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "original_filename",
            "mime_type",
            "size_bytes",
            "extracted_data",
            "owner",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "file": {"write_only": True, "required": False},
        }

    def get_file_url(self, obj):
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_asolute_uri(obj.file.url)
        return obj.file.url
