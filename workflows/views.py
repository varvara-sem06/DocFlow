from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ApprovalRequest, ApprovalRoute
from .serializers import ApprovalRequestSerializer, ApprovalRouteSerializer
from .services import WorkflowError, approve_step, reject_step


class ApprovalRouteViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRoute.objects.filter(is_active=True).prefetch_related("steps")
    serializer_class = ApprovalRouteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApprovalRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApprovalRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return (
            ApprovalRequest.objects.filter(document__owner=user)
            .select_related("document", "route")
            .prefetch_related("actions")
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        instance = self.get_object()
        comment = request.data.get("comment", "")
        try:
            approve_step(instance, request.user, comment)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        instance = self.get_object()
        comment = request.data.get("comment", "")
        try:
            reject_step(instance, request.user, comment)
        except WorkflowError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(instance).data)
