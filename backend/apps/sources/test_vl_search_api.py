import pytest
from django.test import override_settings
from rest_framework.test import APIClient


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="postgres://vl")
def test_vl_search_api_returns_results(monkeypatch):
    monkeypatch.setattr(
        "apps.sources.views.search_vl_documents",
        lambda database_url, query, limit=5, public_base_url="": [
            {
                "id": 10,
                "unit_id": 20,
                "work_id": 30,
                "work_title": "Bhagavad-gita As It Is",
                "document_type": "book",
                "language_code": "en",
                "title": "BG 9.22",
                "body": "Krishna protects His devotee.",
                "date_text": "",
                "metadata": {},
                "public_url": "http://127.0.0.1:3001/texts/20",
            }
        ],
    )

    response = APIClient().get("/api/sources/vl/search?q=Krishna")

    assert response.status_code == 200
    assert response.data["items"][0]["title"] == "BG 9.22"


@pytest.mark.django_db
def test_vl_search_api_requires_query():
    response = APIClient().get("/api/sources/vl/search")

    assert response.status_code == 400
    assert response.data["error"] == "q query parameter is required"
