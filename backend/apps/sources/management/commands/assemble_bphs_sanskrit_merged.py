from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.sources.bphs_sanskrit_merge import assemble_bphs_with_sanskrit


class Command(BaseCommand):
    help = "Assemble normalized BPHS with SanskritDocuments Sanskrit by chapter."

    def add_arguments(self, parser):
        parser.add_argument(
            "--english",
            default="../.private_corpus/bphs-santhanam-normalized.txt",
        )
        parser.add_argument(
            "--sanskrit-root",
            default="../.private_corpus/internet_witnesses",
        )
        parser.add_argument(
            "--output",
            default="../.private_corpus/bphs-santhanam-normalized-with-sanskrit.txt",
        )
        parser.add_argument(
            "--manifest-output",
            default="../.private_corpus/bphs-santhanam-normalized-with-sanskrit-manifest.json",
        )

    def handle(self, *args, **options):
        payload = assemble_bphs_with_sanskrit(
            english_path=Path(options["english"]),
            sanskrit_root=Path(options["sanskrit_root"]),
            output_path=Path(options["output"]),
            manifest_path=Path(options["manifest_output"]),
        )
        self.stdout.write(json.dumps(payload, ensure_ascii=False))
