from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "doc_type", "status", "owner", "created_at")
    list_filter = ("status", "doc_type", "created_at")
    search_fields = ("title", "original_filename", "owner__username")
    readonly_fields = ("created_at", "updated_at", "size_bytes", "mime_type")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
