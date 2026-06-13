from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.sources.citations import combined_citation_search, local_research_corpus_search

from ...codex_cli_generation import (
    generate_birth_chart_codex_cli_analysis,
    generate_compatibility_codex_cli_analysis,
)
from ...models import GeneratedAnalysisDraft, GeneratedAnalysisJob


class Command(BaseCommand):
    help = "Process queued Codex CLI generation jobs."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=1)
        parser.add_argument("--kind")
        parser.add_argument("--skip-evidence-refresh", action="store_true")

    def handle(self, *args, **options):
        limit = max(int(options["limit"] or 1), 1)
        processed = 0
        for job_id in _queued_job_ids(limit=limit, kind=options.get("kind")):
            job = _claim_job(job_id)
            if job is None:
                continue
            processed += 1
            self.stdout.write(f"Processing {job.kind} job #{job.id}")
            _process_job(job, refresh_evidence=not bool(options["skip_evidence_refresh"]))
        self.stdout.write(self.style.SUCCESS(f"Processed {processed} queued Codex job(s)."))


def _queued_job_ids(*, limit: int, kind: str | None = None) -> list[int]:
    jobs = GeneratedAnalysisJob.objects.filter(status=GeneratedAnalysisJob.Status.QUEUED).order_by("created_at", "id")
    if kind:
        jobs = jobs.filter(kind=kind)
    return list(jobs.values_list("id", flat=True)[:limit])


def _claim_job(job_id: int) -> GeneratedAnalysisJob | None:
    with transaction.atomic():
        job = GeneratedAnalysisJob.objects.select_for_update().filter(
            id=job_id,
            status=GeneratedAnalysisJob.Status.QUEUED,
        ).first()
        if job is None:
            return None
        job.status = GeneratedAnalysisJob.Status.RUNNING
        job.started_at = timezone.now()
        job.error = ""
        job.save(update_fields=["status", "started_at", "error", "updated_at"])
        return job


def _process_job(job: GeneratedAnalysisJob, *, refresh_evidence: bool) -> None:
    try:
        output = _generate_for_job(job, refresh_evidence=refresh_evidence)
        analysis_id = output.get("id") if isinstance(output, dict) else None
        job.status = GeneratedAnalysisJob.Status.COMPLETE
        job.completed_at = timezone.now()
        if isinstance(analysis_id, int) and GeneratedAnalysisDraft.objects.filter(id=analysis_id).exists():
            job.analysis_id = analysis_id
        job.save(update_fields=["status", "completed_at", "analysis", "updated_at"])
    except Exception as exc:
        job.status = GeneratedAnalysisJob.Status.FAILED
        job.error = str(exc)[:4000]
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error", "completed_at", "updated_at"])
        raise


def _generate_for_job(job: GeneratedAnalysisJob, *, refresh_evidence: bool) -> dict[str, object]:
    data = job.request_snapshot if isinstance(job.request_snapshot, dict) else {}
    if job.kind == "birth_chart_codex_cli":
        return generate_birth_chart_codex_cli_analysis(
            data,
            citation_search=_vl_citation_search,
            research_search=local_research_corpus_search,
            interpretation_provider=public_interpretation_sections_for_chart,
            refresh_evidence=refresh_evidence,
            force_regenerate=bool(data.get("force_regenerate")),
            user=job.user,
        )
    if job.kind == "compatibility_codex_cli":
        return generate_compatibility_codex_cli_analysis(
            data,
            citation_search=_vl_citation_search,
            research_search=local_research_corpus_search,
            refresh_evidence=refresh_evidence,
            user=job.user,
        )
    raise ValueError(f"Unsupported Codex generation job kind: {job.kind}")


def _vl_citation_search(query: str) -> list[dict[str, object]]:
    return combined_citation_search(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )
