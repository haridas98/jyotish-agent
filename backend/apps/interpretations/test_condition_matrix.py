import pytest
from rest_framework.test import APIClient

from apps.interpretations.condition_matrix import shastra_condition_matrix
from apps.interpretations.yoga_catalog import yoga_registry
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_shastra_condition_matrix_lists_calculation_layers_and_all_yogas_with_coverage():
    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body="Gaja Kesari candidate condition.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )

    matrix = shastra_condition_matrix()

    assert matrix["schema_version"] == "jyotish-shastra-condition-matrix-v1"
    assert matrix["summary"]["yoga_conditions"] == len(yoga_registry())
    assert matrix["summary"]["total_conditions"] > matrix["summary"]["yoga_conditions"]
    yoga_rows = [row for row in matrix["conditions"] if row["kind"] == "yoga_condition"]
    assert any(row["key"] == "gaja_kesari" for row in yoga_rows)
    assert all(row["source_priority"] for row in yoga_rows)
    gaja = next(row for row in yoga_rows if row["key"] == "gaja_kesari")
    assert gaja["public_release_policy"] == "needs_approved_passage"
    assert gaja["coverage_status"] in {"research_only_available", "private_text_loaded"}
    assert "Gaja Kesari Phaladipika" in gaja["search_queries"]


@pytest.mark.django_db
def test_shastra_condition_matrix_api_returns_conditions():
    response = APIClient().get("/api/reports/shastra-condition-matrix")

    assert response.status_code == 200
    assert response.json()["summary"]["total_conditions"] > 0
