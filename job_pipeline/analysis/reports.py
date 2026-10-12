"""Analyze recent search candidates. / 최근 검색 후보를 분석해 저장합니다."""

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys

from job_pipeline.paths import ROOT
from job_pipeline.records import AnalysisResult, SavedJobAnalysis, parse_source_metadata
from job_pipeline.analysis.extraction import analyze_posting


SEARCH_DIR = ROOT / "data" / "results" / "search_probe"
ATS_DIR = ROOT / "data" / "results" / "ats_collection"
ANALYSES_DIR = ROOT / "data" / "results" / "analyses" / "search"


def checked_time(value: object) -> datetime | None:
    """Parse an aware check time. / 시간대가 있는 확인 시각만 읽습니다."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def deadline_status(value: object, now: datetime) -> str:
    """Classify a published deadline. / 공개된 마감일의 경과 여부를 분류합니다."""
    if not isinstance(value, str) or not value:
        return "unknown"
    try:
        if "T" in value:
            deadline = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if deadline.tzinfo is None:
                return "unknown"
            return "past" if deadline < now else "future_or_now"
        deadline_day = date.fromisoformat(value)
        return "past" if deadline_day < now.date() else "future_or_today"
    except ValueError:
        return "unknown"


def analyze_file(path: Path, model: str) -> AnalysisResult:
    """Read a posting and call Ollama directly. / 공고를 읽고 Ollama 분석 함수를 직접 호출합니다."""
    return analyze_posting(path.read_text(encoding="utf-8"), model)


def analyze_report(
    report_path: Path, model: str, limit: int, max_age_hours: int
) -> tuple[int, int]:
    """Analyze recent candidates and save them. / 최근 후보를 분석해 저장합니다."""
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, list):
        raise ValueError("Search report must be a JSON array")

    now = datetime.now(timezone.utc)
    saved = 0
    failed = 0
    for item in report:
        if saved >= limit:
            break
        if not isinstance(item, dict) or item.get("status") != "text_extracted":
            continue
        if item.get("job_candidate") is not True:
            print(f"Skipped unverified job page: {item.get('url', '')}")
            continue
        if item.get("availability") == "closed":
            print(f"Skipped closed page: {item.get('url', '')}")
            continue
        checked = checked_time(item.get("checked_at_utc"))
        if checked is None or not timedelta(0) <= now - checked <= timedelta(hours=max_age_hours):
            print(f"Skipped stale or undated page: {item.get('url', '')}")
            continue
        deadline = item.get("deadline_at")
        deadline_state = deadline_status(deadline, now)
        if deadline_state == "past":
            print(f"Skipped past deadline: {item.get('url', '')}")
            continue
        url = item.get("url")
        text_file = item.get("text_file")
        if not isinstance(url, str) or not isinstance(text_file, str):
            print("Skipped search result without a URL or text file.", file=sys.stderr)
            failed += 1
            continue
        path = (ROOT / text_file).resolve()
        if not (path.is_relative_to(SEARCH_DIR.resolve()) or path.is_relative_to(ATS_DIR.resolve())) or not path.is_file():
            print(f"Invalid text file for {url}", file=sys.stderr)
            failed += 1
            continue
        try:
            analysis = analyze_file(path, model)
            source: dict[str, object] = {
                "source_url": url,
                "fetched_at_utc": checked.isoformat(),
                "discovery": item.get("discovery") if isinstance(item.get("discovery"), str) else "ddgs",
                "posted_at": item.get("posted_at") if isinstance(item.get("posted_at"), str) else None,
                "deadline_at": deadline if isinstance(deadline, str) else None,
                "deadline_status": deadline_state,
                "availability": item.get("availability") if isinstance(item.get("availability"), str) else "accessible_unverified",
            }
            record: SavedJobAnalysis = {
                "source": parse_source_metadata(source),
                "model": model,
                "analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
                "analysis": analysis,
            }
            file_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
            output = ANALYSES_DIR / f"{file_id}.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            print(f"Cannot analyze {url}: {error}", file=sys.stderr)
            failed += 1
            continue
        saved += 1
        print(f"Saved analysis: {output}")
        print(f"Original posting: {url}")

    print(f"Saved: {saved}, failed: {failed}")
    return saved, failed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze recent ATS or DDGS candidates and save results."
    )
    parser.add_argument(
        "--report", type=Path, default=SEARCH_DIR / "latest.json", help="Search probe report"
    )
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model name")
    parser.add_argument("--limit", type=int, default=1, help="Maximum candidates to analyze")
    parser.add_argument(
        "--max-age-hours", type=int, default=24, help="Maximum age of a page check"
    )
    args = parser.parse_args()
    if args.limit < 1 or args.max_age_hours < 1:
        parser.error("--limit and --max-age-hours must be positive")

    try:
        _, failed = analyze_report(args.report, args.model, args.limit, args.max_age_hours)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Cannot read search report: {error}", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
