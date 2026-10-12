"""Coordinate collection and analysis outside HTTP requests. / 웹 요청 밖에서 수집·분석 흐름을 조율합니다."""

from dataclasses import dataclass
from pathlib import Path
import sys

from job_pipeline.paths import DEFAULT_CONFIG, DEFAULT_QUERY_CONFIG, DEFAULT_PROFILE_CONFIG
from job_pipeline.records import CATEGORIES, STATUSES


@dataclass(frozen=True)
class PipelineOptions:
    """Options shared by CLI and the worker's child process. / CLI와 작업자의 자식 프로세스가 공유하는 실행 설정입니다."""

    source: str = "ats"
    query: str | None = None
    config: Path = DEFAULT_CONFIG
    queries_file: Path = DEFAULT_QUERY_CONFIG
    profile: Path = DEFAULT_PROFILE_CONFIG
    discover: bool = False
    search_limit: int = 5
    analyze_limit: int = 1
    model: str = "qwen3:8b"
    max_age_hours: int = 24
    category: str | None = None
    status: str | None = None


def validate_options(options: PipelineOptions) -> None:
    """Share option validation between CLI and programmatic callers. / CLI·함수 호출이 공유하는 옵션 검증입니다."""
    if options.source not in ("ats", "ddgs"):
        raise ValueError("Source must be ats or ddgs")
    if options.search_limit < 1 or (options.source == "ddgs" and options.search_limit > 10):
        raise ValueError("Search limit must be positive (DDGS maximum: 10)")
    if options.analyze_limit < 1 or options.max_age_hours < 1:
        raise ValueError("Analysis limit and maximum age must be positive")
    if options.category is not None and options.category not in CATEGORIES:
        raise ValueError("Invalid category")
    if options.status is not None and (options.category is None or options.status not in STATUSES):
        raise ValueError("A valid status requires a category")
    if options.source == "ddgs" and not options.query:
        raise ValueError("DDGS mode requires a query")
    if options.discover and options.source != "ats":
        raise ValueError("Discovery requires ATS mode")


def run_pipeline(options: PipelineOptions) -> int:
    """Run ATS/DDGS → Ollama → JSON → CLI listing; return an exit code. / ATS·DDGS → Ollama → JSON → CLI 조회를 실행하고 종료 코드를 반환합니다."""
    validate_options(options)
    # Import integrations only when collection runs. / 실제 수집 실행 시 외부 연동 모듈을 불러옵니다.
    from job_pipeline.analysis.reports import analyze_report
    from job_pipeline.collection import collect_jobs
    from job_pipeline.discovery.boards import discover_adaptively
    from job_pipeline.search import search_jobs
    from job_pipeline.storage import list_analyses

    print("Collecting job postings...")
    try:
        if options.source == "ats":
            if options.discover:
                discover_adaptively(options.config, 5, None, options.queries_file, options.profile, options.model)
            report_path, extracted, board_failures = collect_jobs(options.config, options.search_limit)
        else:
            report_path, _, extracted = search_jobs(options.query or "", options.search_limit)
            board_failures = 0
    except Exception as error:
        print(f"Search failed: {error}", file=sys.stderr)
        return 1
    if extracted == 0:
        print("No page text was extracted; there is nothing to analyze.")
        return 1 if board_failures else 0

    print("Analyzing recent job candidates...")
    try:
        saved, failed = analyze_report(report_path, options.model, options.analyze_limit, options.max_age_hours)
    except (OSError, ValueError) as error:
        print(f"Cannot analyze search report: {error}", file=sys.stderr)
        return 1
    if saved == 0:
        print("No eligible candidate was saved from this search.")
    print("Saved analyses (including previous runs):")
    listed = list_analyses(options.category, options.status)
    return 1 if failed or listed or board_failures else 0
