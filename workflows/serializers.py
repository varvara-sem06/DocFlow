from rest_framework import serializers

from .models import ApprovalAction, ApprovalRequest, ApprovalRoute, ApprovalStep


class ApprovalStepSerializer(serializers.ModelSerializer):
    approver_username = serializers.CharField(source="approver.username", read_only=True)

    class Meta:
        model = ApprovalStep
        fields = ["id", "order", "approver", "approver_username", "is_required"]


class ApprovalRouteSerializer(serializers.ModelSerializer):
    steps = ApprovalStepSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalRoute
        fields = [
            "id",
            "name",
            "description",
            "doc_type",
            "is_active",
            "created_by",
            "created_at",
            "steps",
        ]
        read_only_fields = ["created_by", "created_at"]


class ApprovalActionSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = ApprovalAction
        fields = [
            "id",
            "user",
            "user_username",
            "action",
            "action_display",
            "comment",
            "created_at",
        ]


class ApprovalRequestSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True)
    route_name = serializers.CharField(source="route.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    actions = ApprovalActionSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            "id",
            "document",
            "document_title",
            "route",
            "route_name",
            "status",
            "status_display",
            "current_step",
            "started_by",
            "started_at",
            "finished_at",
            "actions",
        ]
        read_only_fields = [
            "status",
            "current_step",
            "started_by",
            "started_at",
            "finished_at",
        ]
