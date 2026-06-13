from __future__ import annotations

from django.conf import settings
from django.db import models


class Place(models.Model):
    external_id = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=2, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timezone_name = models.CharField(max_length=128)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["external_id"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.latitude}, {self.longitude})"


class BirthProfile(models.Model):
    class TimeAccuracy(models.TextChoices):
        EXACT = "exact", "Exact"
        APPROXIMATE = "approximate", "Approximate"
        UNKNOWN = "unknown", "Unknown"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    birth_time = models.TimeField(null=True, blank=True)
    birth_time_accuracy = models.CharField(
        max_length=32,
        choices=TimeAccuracy.choices,
        default=TimeAccuracy.EXACT,
    )
    place = models.ForeignKey(Place, on_delete=models.PROTECT)
    timezone_name = models.CharField(max_length=128)
    calculation_settings = models.JSONField(default=dict, blank=True)
    is_self_profile = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["birth_date"]),
        ]

    def __str__(self) -> str:
        return self.display_name


class BirthProfileRelationship(models.Model):
    class Role(models.TextChoices):
        PARTNER = "partner", "Partner"
        FATHER = "father", "Father"
        MOTHER = "mother", "Mother"
        BROTHER = "brother", "Brother"
        SISTER = "sister", "Sister"
        SIBLING = "sibling", "Sibling"
        BOSS = "boss", "Boss"
        SUBORDINATE = "subordinate", "Subordinate"
        OPPONENT = "opponent", "Opponent"
        OTHER = "other", "Other"

    class LinkStatus(models.TextChoices):
        PRIVATE = "private", "Private saved relation"
        REQUESTED = "requested", "User link requested"
        ACCEPTED = "accepted", "User link accepted"
        DECLINED = "declined", "User link declined"
        BLOCKED = "blocked", "User link blocked"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="birth_profile_relationships")
    profile = models.ForeignKey(BirthProfile, on_delete=models.CASCADE, related_name="outgoing_relationships")
    related_profile = models.ForeignKey(BirthProfile, on_delete=models.CASCADE, related_name="incoming_relationships")
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.PARTNER)
    link_status = models.CharField(max_length=32, choices=LinkStatus.choices, default=LinkStatus.PRIVATE)
    requested_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="birth_profile_relationship_requests",
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "profile", "related_profile"], name="unique_birth_profile_relationship"),
            models.CheckConstraint(condition=~models.Q(profile=models.F("related_profile")), name="birth_profile_relationship_not_self"),
        ]
        indexes = [
            models.Index(fields=["user", "role"]),
            models.Index(fields=["user", "link_status"]),
            models.Index(fields=["user", "updated_at"], name="charts_rel_user_updated_idx"),
            models.Index(fields=["requested_user", "link_status"]),
            models.Index(fields=["requested_user", "link_status", "updated_at"], name="charts_rel_inbox_updated_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}->{self.related_profile_id}:{self.role}:{self.link_status}"


class ChartCalculation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETE = "complete", "Complete"
        FAILED = "failed", "Failed"

    profile = models.ForeignKey(BirthProfile, on_delete=models.CASCADE, related_name="calculations")
    calculation_version = models.CharField(max_length=64)
    ayanamsa = models.CharField(max_length=64, default="lahiri")
    house_system = models.CharField(max_length=64, default="whole_sign")
    input_snapshot = models.JSONField(default=dict)
    result = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["profile", "created_at"]),
            models.Index(fields=["calculation_version"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.calculation_version}:{self.status}"


class PlanetPosition(models.Model):
    calculation = models.ForeignKey(
        ChartCalculation,
        on_delete=models.CASCADE,
        related_name="planet_positions",
    )
    graha = models.CharField(max_length=32)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    speed = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    rashi = models.CharField(max_length=32)
    nakshatra = models.CharField(max_length=64)
    pada = models.PositiveSmallIntegerField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("calculation", "graha")]
        indexes = [
            models.Index(fields=["graha"]),
            models.Index(fields=["rashi"]),
            models.Index(fields=["nakshatra"]),
        ]


class VargaPlacement(models.Model):
    calculation = models.ForeignKey(
        ChartCalculation,
        on_delete=models.CASCADE,
        related_name="varga_placements",
    )
    varga = models.CharField(max_length=16)
    graha = models.CharField(max_length=32)
    rashi = models.CharField(max_length=32)
    house = models.PositiveSmallIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("calculation", "varga", "graha")]
        indexes = [
            models.Index(fields=["varga"]),
            models.Index(fields=["graha"]),
        ]


class DashaPeriod(models.Model):
    calculation = models.ForeignKey(
        ChartCalculation,
        on_delete=models.CASCADE,
        related_name="dasha_periods",
    )
    system = models.CharField(max_length=64)
    level = models.PositiveSmallIntegerField()
    lord = models.CharField(max_length=32)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["system", "level"]),
            models.Index(fields=["starts_at", "ends_at"]),
        ]
