from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("timeline/", views.timeline, name="timeline"),
    path("top-counterparties/", views.top_counterparties_view, name="top-counterparties"),
    path("users-activity/", views.users_activity_view, name="users-activity"),
    path("export/documents.xlsx", views.export_documents, name="export-documents"),
]
