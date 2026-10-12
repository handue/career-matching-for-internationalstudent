"""Parse CLI options for the shared pipeline. / 공통 처리 흐름에 전달할 CLI 옵션을 읽습니다."""

import argparse
from pathlib import Path
import sys


from job_pipeline.paths import DEFAULT_CONFIG, DEFAULT_QUERY_CONFIG, DEFAULT_PROFILE_CONFIG
from job_pipeline.pipeline import PipelineOptions, run_pipeline, validate_options
from job_pipeline.records import CATEGORIES, STATUSES



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search, analyze, save, and list job candidates."
    )
    parser.add_argument("--source", choices=("ats", "ddgs"), default="ats", help="Posting discovery source")
    parser.add_argument("--query", help="Manual search query for DDGS mode")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="ATS board configuration")
    parser.add_argument("--queries-file", type=Path, default=DEFAULT_QUERY_CONFIG, help="ATS discovery query configuration")
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE_CONFIG, help="Search profile for ATS discovery")
    parser.add_argument("--discover", action="store_true", help="Discover new ATS boards before collection")
    parser.add_argument(
        "--search-limit", type=int, default=5, help="Maximum postings to collect (DDGS: 1-10)"
    )
    parser.add_argument(
        "--analyze-limit", type=int, default=1, help="Maximum candidates to analyze"
    )
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model name")
    parser.add_argument(
        "--max-age-hours", type=int, default=24, help="Maximum age of a page check"
    )
    parser.add_argument("--category", choices=CATEGORIES, help="Category to list")
    parser.add_argument("--status", choices=STATUSES, help="Status to list")
    args = parser.parse_args()
    options = PipelineOptions(
        source=args.source, query=args.query, config=args.config,
        queries_file=args.queries_file, profile=args.profile, discover=args.discover,
        search_limit=args.search_limit, analyze_limit=args.analyze_limit,
        model=args.model, max_age_hours=args.max_age_hours,
        category=args.category, status=args.status,
    )
    try:
        validate_options(options)
    except ValueError as error:
        parser.error(str(error))
    return run_pipeline(options)


if __name__ == "__main__":
    sys.exit(main())
