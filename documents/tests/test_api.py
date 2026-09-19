import pytest

from documents.models import Document


@pytest.mark.django_db
class TestDocumentAPI:
    def test_list_requires_auth(self, api_client):
        r = api_client.get("/api/documents/")
        assert r.status_code == 401

    def test_list_returns_own_docs_only(self, auth_client, user, another_user):
        Document.objects.create(title="Мой", owner=user)
        Document.objects.create(title="Чужой", owner=another_user)

        r = auth_client.get("/api/documents/")
        assert r.status_code == 200
        titles = [d["title"] for d in r.json()["results"]]
        assert "Мой" in titles
        assert "Чужой" not in titles

    def test_create_sets_owner(self, auth_client, user):
        r = auth_client.post(
            "/api/documents/",
            {"title": "Новый", "doc_type": "invoice"},
            format="json",
        )
        assert r.status_code == 201
        doc = Document.objects.get(id=r.json()["id"])
        assert doc.owner == user
