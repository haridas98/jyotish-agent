from __future__ import annotations


def ps_quote(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"
