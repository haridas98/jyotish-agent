from __future__ import annotations

from django.conf import settings
from django.db import models


class UserJyotishSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="jyotish_settings",
    )
    calculation = models.JSONField(default=dict, blank=True)
    display = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"jyotish-settings:{self.user_id}"
