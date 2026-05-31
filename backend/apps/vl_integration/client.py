from __future__ import annotations

import psycopg


def check_vl_database(database_url: str) -> dict[str, object]:
    if not database_url:
        return {
            "status": "not_configured",
            "database": "vl",
            "detail": "VL_DATABASE_URL is empty",
        }

    try:
        with psycopg.connect(database_url, connect_timeout=3) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                      (SELECT COUNT(*) FROM works) AS works,
                      (SELECT COUNT(*) FROM text_units) AS text_units,
                      (SELECT COUNT(*) FROM search_documents) AS search_documents
                    """
                )
                works, text_units, search_documents = cursor.fetchone()
    except Exception as exc:
        return {
            "status": "error",
            "database": "vl",
            "detail": str(exc),
        }

    return {
        "status": "ok",
        "database": "vl",
        "works": works,
        "text_units": text_units,
        "search_documents": search_documents,
    }

