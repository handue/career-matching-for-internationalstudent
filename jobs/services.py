"""Bridge existing analysis files into Django's DB. / 기존 분석 파일을 Django DB에 연결합니다."""
import json
from pathlib import Path
from django.conf import settings
from job_pipeline.records import parse_saved_job_analysis
from .models import JobAnalysis


def import_analyses(directory: Path | None = None) -> tuple[int, int]:
    """Validate local JSON files and upsert by source URL. / 로컬 JSON을 검증하고 원문 URL로 중복 없이 저장합니다."""
    directory = directory or settings.BASE_DIR / "data" / "results" / "analyses"
    imported = failed = 0
    for path in sorted(directory.rglob("*.json")):
        try:
            record = parse_saved_job_analysis(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError, TypeError, KeyError):
            failed += 1
            continue
        analysis = record["analysis"]
        JobAnalysis.objects.update_or_create(source_url=record["source"]["source_url"], defaults={
            "title": analysis["title"], "company": analysis["company"],
            "location": analysis["location"], "record": record,
        })
        imported += 1
    return imported, failed
