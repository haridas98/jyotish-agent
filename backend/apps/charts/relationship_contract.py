from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from django.conf import settings


@lru_cache(maxsize=1)
def relationship_contract() -> dict[str, Any]:
    path = Path(settings.ROOT_DIR) / "shared" / "contracts" / "relationship-types.json"
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    relationship_types = {item["id"]: item for item in raw["relationshipTypes"]}
    return {
        "roles": set(raw["roles"]),
        "relationship_types": relationship_types,
    }


def get_relationship_type_contract(relationship_type_id: str) -> dict[str, Any] | None:
    return relationship_contract()["relationship_types"].get(relationship_type_id)


def is_known_role(role_id: str) -> bool:
    return role_id in relationship_contract()["roles"]
