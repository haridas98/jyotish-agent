from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BirthProfile, ChartCalculation
from .services import (
    ChartProfileInputError,
    calculate_profile_chart,
    calculation_payload,
    create_birth_profile,
    profile_payload,
)


class BirthProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profiles = (
            BirthProfile.objects.filter(user=request.user).select_related("place").order_by("-created_at")
        )
        return Response({"profiles": [profile_payload(profile) for profile in profiles]})

    def post(self, request):
        try:
            profile = create_birth_profile(request.user, request.data)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"profile": profile_payload(profile)}, status=201)


class BirthProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        return Response({"profile": profile_payload(profile)})


class BirthProfileCalculateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        calculation = calculate_profile_chart(profile)
        status_code = 201 if calculation.status == ChartCalculation.Status.COMPLETE else 503
        return Response({"calculation": calculation_payload(calculation)}, status=status_code)
