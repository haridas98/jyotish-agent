from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess

from .models import BirthProfile, BirthProfileRelationship, ChartCalculation
from .services import (
    ChartProfileInputError,
    calculate_profile_chart,
    calculation_payload,
    create_birth_profile,
    list_incoming_profile_relationship_requests,
    list_profile_relationships,
    profile_payload,
    profiles_payload,
    profile_relationship_payload,
    update_birth_profile_flags,
    update_incoming_profile_relationship_request,
    upsert_profile_relationship,
)


class BirthProfileListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        profiles = (
            BirthProfile.objects.filter(user=request.user).select_related("place").order_by("-created_at")
        )
        return Response({"profiles": profiles_payload(list(profiles))})

    def post(self, request):
        try:
            profile = create_birth_profile(request.user, request.data)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"profile": profile_payload(profile)}, status=201)


class BirthProfileDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        return Response({"profile": profile_payload(profile)})

    def patch(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        try:
            profile = update_birth_profile_flags(profile, request.data)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"profile": profile_payload(profile)})

    def delete(self, request, profile_id: int):
        profile = get_object_or_404(BirthProfile, id=profile_id, user=request.user)
        profile.delete()
        return Response(status=204)


class BirthProfileCalculateView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        calculation = calculate_profile_chart(profile, reuse_existing=True)
        if getattr(calculation, "_jyotish_reused", False):
            status_code = 200
        else:
            status_code = 201 if calculation.status == ChartCalculation.Status.COMPLETE else 503
        return Response({"calculation": calculation_payload(calculation)}, status=status_code)


class BirthProfileRelationshipListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        relationships = list_profile_relationships(request.user)
        return Response({"relationships": [profile_relationship_payload(item) for item in relationships]})

    def post(self, request):
        try:
            relationship = upsert_profile_relationship(request.user, request.data)
        except BirthProfile.DoesNotExist:
            return Response({"error": "profile not found"}, status=404)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": profile_relationship_payload(relationship)}, status=201)


class BirthProfileRelationshipInboxView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        requests = list_incoming_profile_relationship_requests(request.user)
        return Response({"relationships": [profile_relationship_payload(item) for item in requests]})


class BirthProfileRelationshipDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, relationship_id: int):
        relationship = get_object_or_404(
            BirthProfileRelationship.objects.select_related(
                "user",
                "profile",
                "related_profile",
                "requested_user",
                "profile__place",
                "related_profile__place",
            ),
            id=relationship_id,
            user=request.user,
        )
        return Response({"relationship": profile_relationship_payload(relationship)})

    def delete(self, request, relationship_id: int):
        relationship = get_object_or_404(BirthProfileRelationship, id=relationship_id, user=request.user)
        relationship.delete()
        return Response(status=204)


class BirthProfileRelationshipActionView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request, relationship_id: int):
        try:
            relationship = update_incoming_profile_relationship_request(
                request.user,
                relationship_id,
                str(request.data.get("action") or "").strip(),
                request.data,
            )
        except BirthProfileRelationship.DoesNotExist:
            return Response({"error": "relationship request not found"}, status=404)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": profile_relationship_payload(relationship)})
