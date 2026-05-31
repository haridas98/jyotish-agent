from apps.vl_integration.client import search_vl_documents


def test_search_vl_documents_returns_structured_rows(monkeypatch):
    calls = []

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, sql, params):
            calls.append((sql, params))

        def fetchall(self):
            return [
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
                    "metadata": {"slug": "bg-9-22"},
                }
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def cursor(self, *args, **kwargs):
            return FakeCursor()

    monkeypatch.setattr("apps.vl_integration.client.psycopg.connect", lambda *args, **kwargs: FakeConnection())

    results = search_vl_documents("postgres://vl", "Krishna protects", limit=3)

    assert results == [
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
            "metadata": {"slug": "bg-9-22"},
            "public_url": "http://127.0.0.1:3001/texts/20",
        }
    ]
    assert calls[0][1]["query"] == "Krishna protects"
    assert calls[0][1]["limit"] == 3


def test_search_vl_documents_returns_empty_when_not_configured():
    assert search_vl_documents("", "Krishna") == []
