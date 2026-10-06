"""Save one analyzed Greenhouse posting. / Greenhouse 공고 한 건의 분석 결과를 저장합니다."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

from job_record import SavedJobAnalysis, parse_analysis_result, parse_source_metadata


ROOT: Path = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze a saved Greenhouse posting and save its JSON result."
    )
    parser.add_argument("--board", required=True, help="Greenhouse board token")
    parser.add_argument("--job-id", required=True, type=int, help="Greenhouse job post ID")
    parser.add_argument("--model", default="qwen3:8b", help="Ollama model name")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.board) or args.job_id <= 0:
        print("Invalid board token or job ID.", file=sys.stderr)
        return 1

    fetched_dir = ROOT / "data" / "results" / "greenhouse" / args.board
    posting_path = fetched_dir / f"{args.job_id}.txt"
    metadata_path = fetched_dir / f"{args.job_id}.json"
    try:
        # Preserve the source URL and fetch time. / 원문 URL과 수집 시각을 함께 보존합니다.
        metadata = parse_source_metadata(
            json.loads(metadata_path.read_text(encoding="utf-8"))
        )
        if metadata["board"] != args.board or metadata["job_id"] != args.job_id:
            raise ValueError("Source metadata does not match the requested job")
        if not posting_path.is_file():
            raise FileNotFoundError(posting_path)

        command = [
            sys.executable,
            str(ROOT / "scripts" / "analyze_job.py"),
            "--model",
            args.model,
            "--file",
            str(posting_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=330)
        if completed.returncode != 0:
            print(completed.stderr.strip() or "Job analysis failed.", file=sys.stderr)
            return 1

        # The analyzer prints JSON followed by elapsed time. / 분석기는 JSON 다음에 실행 시간을 출력합니다.
        parsed_output, _ = json.JSONDecoder().raw_decode(completed.stdout)
        analysis = parse_analysis_result(parsed_output)
        record: SavedJobAnalysis = {
            "source": metadata,
            "model": args.model,
            "analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
            "analysis": analysis,
        }
        output = ROOT / "data" / "results" / "analyses" / args.board / f"{args.job_id}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
        print(f"Cannot save analysis: {error}", file=sys.stderr)
        return 1

    print(f"Saved analysis: {output}")
    print(f"Original posting: {metadata['source_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
