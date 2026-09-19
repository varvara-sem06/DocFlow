from rest_framework.routers import DefaultRouter

from .views import ApprovalRequestViewSet, ApprovalRouteViewSet

router = DefaultRouter()
router.register(r"routes", ApprovalRouteViewSet, basename="route")
router.register(r"requests", ApprovalRequestViewSet, basename="request")

urlpatterns = router.urls
