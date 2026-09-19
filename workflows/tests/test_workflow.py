import pytest

from documents.models import Document
from workflows.models import ApprovalRoute, ApprovalStep
from workflows.services import WorkflowError, approve_step, start_approval


@pytest.mark.django_db
class TestWorkflow:
    def _make_route(self, user, steps=2):
        route = ApprovalRoute.objects.create(name="Тест", created_by=user)
        for i in range(1, steps + 1):
            ApprovalStep.objects.create(route=route, order=i, approver=user)
        return route

    def test_start_approval(self, user):
        doc = Document.objects.create(title="X", owner=user)
        route = self._make_route(user)
        req = start_approval(doc, route, user)

        doc.refresh_from_db()
        assert doc.status == Document.Status.ON_APPROVAL
        assert req.current_step == 1
        assert req.status == "pending"

    def test_approve_full_route(self, user):
        doc = Document.objects.create(title="X", owner=user)
        route = self._make_route(user, steps=2)
        req = start_approval(doc, route, user)

        approve_step(req, user)
        req.refresh_from_db()
        assert req.current_step == 2

        approve_step(req, user)
        req.refresh_from_db()
        doc.refresh_from_db()
        assert req.status == "approved"
        assert doc.status == Document.Status.APPROVED

    def test_reject_stops_workflow(self, user):
        doc = Document.objects.create(title="X", owner=user)
        route = self._make_route(user)
        req = start_approval(doc, route, user)

        from workflows.services import reject_step

        reject_step(req, user, comment="Не то")

        req.refresh_from_db()
        doc.refresh_from_db()
        assert req.status == "rejected"
        assert doc.status == Document.Status.REJECTED

    def test_wrong_user_cannot_approve(self, user, another_user):
        doc = Document.objects.create(title="X", owner=user)
        route = self._make_route(user)
        req = start_approval(doc, route, user)

        with pytest.raises(WorkflowError):
            approve_step(req, another_user)
