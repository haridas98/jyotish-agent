from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import BasePermission


class PrivateAppAccess(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not getattr(settings, "PRIVATE_APP_REQUIRE_AUTH", False):
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
