from __future__ import annotations

import psycopg
from psycopg.rows import dict_row


DEFAULT_VL_PUBLIC_BASE_URL = "http://127.0.0.1:3001"


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


def search_vl_documents(
    database_url: str,
    query: str,
    limit: int = 5,
    public_base_url: str = DEFAULT_VL_PUBLIC_BASE_URL,
) -> list[dict[str, object]]:
    query = query.strip()
    if not database_url or not query:
        return []

    with psycopg.connect(database_url, connect_timeout=3) as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                  sd.id,
                  sd.unit_id,
                  sd.work_id,
                  w.title AS work_title,
                  sd.document_type,
                  sd.language_code,
                  sd.title,
                  left(sd.body, 600) AS body,
                  sd.date_text,
                  sd.metadata
                FROM search_documents sd
                LEFT JOIN works w ON w.id = sd.work_id
                WHERE sd.tsv @@ plainto_tsquery('simple', %(query)s)
                   OR lower(sd.title_ascii) LIKE lower(%(like_query)s)
                   OR lower(sd.body_ascii) LIKE lower(%(like_query)s)
                ORDER BY ts_rank(sd.tsv, plainto_tsquery('simple', %(query)s)) DESC, sd.id ASC
                LIMIT %(limit)s
                """,
                {
                    "query": query,
                    "like_query": f"%{query}%",
                    "limit": max(1, min(int(limit), 20)),
                },
            )
            rows = cursor.fetchall()

    return [_vl_search_payload(row, public_base_url) for row in rows]


def _vl_search_payload(row: dict[str, object], public_base_url: str) -> dict[str, object]:
    unit_id = row.get("unit_id")
    return {
        "id": row["id"],
        "unit_id": unit_id,
        "work_id": row.get("work_id"),
        "work_title": row.get("work_title") or "",
        "document_type": row.get("document_type") or "",
        "language_code": row.get("language_code") or "",
        "title": row.get("title") or "",
        "body": row.get("body") or "",
        "date_text": row.get("date_text") or "",
        "metadata": row.get("metadata") or {},
        "public_url": f"{public_base_url.rstrip('/')}/texts/{unit_id}" if unit_id else "",
    }
