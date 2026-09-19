import pytest

from documents.models import Document


@pytest.mark.django_db
class TestDocumentModel:
    def test_create_document(self, user):
        doc = Document.objects.create(title="Счёт", owner=user)
        assert doc.status == Document.Status.DRAFT
        assert doc.doc_type == Document.DocType.OTHER
        assert str(doc).startswith("Счёт")

    def test_default_extracted_data(self, user):
        doc = Document.objects.create(title="X", owner=user)
        assert doc.extracted_data == {}
