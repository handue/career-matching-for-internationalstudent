"""List saved analyses by category and status. / 저장된 분석을 항목과 상태로 조회합니다."""

import argparse
import json
import sys

from job_pipeline.paths import ROOT
from job_pipeline.records import CATEGORIES, STATUSES, Status, parse_saved_job_analysis


def list_analyses(category: str | None = None, status: str | None = None) -> int:
    """Print saved analyses. / 저장된 공고 분석을 출력합니다."""
    results_dir = ROOT / "data" / "results" / "analyses"
    count = 0
    for path in sorted(results_dir.rglob("*.json")):
        try:
            record = parse_saved_job_analysis(
                json.loads(path.read_text(encoding="utf-8"))
            )
            source = record["source"]
            analysis = record["analysis"]
            source_url = source["source_url"]
            title = analysis["title"]
            company = analysis["company"]
            # TypedDict keys are explicit, so Pylance can check each field. / 키를 명시해 타입 검사를 받습니다.
            statuses: dict[str, Status] = {
                "cpt": analysis["cpt_status"],
                "opt": analysis["opt_status"],
                "stem_opt": analysis["stem_opt_status"],
                "visa_sponsorship": analysis["visa_sponsorship_status"],
                "h1b": analysis["h1b_status"],
                "green_card": analysis["green_card_status"],
            }
            if category and status and statuses[category] != status:
                continue
            evidence_by_category: dict[str, str] = {
                "cpt": analysis["cpt_evidence"],
                "opt": analysis["opt_evidence"],
                "stem_opt": analysis["stem_opt_evidence"],
                "visa_sponsorship": analysis["visa_sponsorship_evidence"],
                "h1b": analysis["h1b_evidence"],
                "green_card": analysis["green_card_evidence"],
            }
            evidence = evidence_by_category[category] if category else None
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            print(f"Invalid saved analysis {path}: {error}", file=sys.stderr)
            return 1

        count += 1
        print(f"{title} | {company}")
        print("  " + ", ".join(f"{category}={statuses[category]}" for category in CATEGORIES))
        if evidence:
            print(f"  Evidence: {evidence}")
        if source.get("discovery") == "ddgs":
            print(f"  Availability: {source.get('availability', 'unknown')}")
            print(f"  Deadline: {source.get('deadline_at') or 'unknown'} ({source.get('deadline_status', 'unknown')})")
        print(f"  Source: {source_url}")
    print(f"Matching jobs: {count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="List saved job analyses.")
    parser.add_argument("--category", choices=CATEGORIES, help="Category to filter")
    parser.add_argument("--status", choices=STATUSES, help="Status to match in the category")
    args = parser.parse_args()
    if args.status and not args.category:
        parser.error("--status requires --category")
    return list_analyses(args.category, args.status)


if __name__ == "__main__":
    sys.exit(main())
