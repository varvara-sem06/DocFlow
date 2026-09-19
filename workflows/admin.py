from django.contrib import admin

from .models import ApprovalAction, ApprovalRequest, ApprovalRoute, ApprovalStep


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 1


@admin.register(ApprovalRoute)
class ApprovalRouteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "doc_type", "is_active", "created_at")
    list_filter = ("is_active", "doc_type")
    search_fields = ("name",)
    inlines = [ApprovalStepInline]


class ApprovalActionInline(admin.TabularInline):
    model = ApprovalAction
    extra = 0
    readonly_fields = ("user", "action", "comment", "created_at")
    can_delete = False


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "route", "status", "current_step", "started_at")
    list_filter = ("status", "route")
    search_fields = ("document__title",)
    inlines = [ApprovalActionInline]


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "order", "approver", "is_required")
    list_filter = ("route", "is_required")


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "user", "action", "created_at")
    list_filter = ("action",)
