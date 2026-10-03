"""Compare sample answers with model output. / 샘플 정답과 모델 출력을 비교합니다."""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("cpt", "opt", "stem_opt", "visa_sponsorship", "h1b", "green_card")


def main():
    expected = json.loads((ROOT / "samples" / "expected_statuses.json").read_text(encoding="utf-8"))
    sample_names = {path.name for path in (ROOT / "samples").glob("*.txt")}
    missing = sample_names - expected.keys()
    if missing:
        print("Missing answer keys: {}".format(", ".join(sorted(missing))))
        return 1
    failures = 0
    for filename, answer in expected.items():
        command = [sys.executable, str(ROOT / "scripts" / "analyze_job.py"),
                   "--file", str(ROOT / "samples" / filename)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=330)
        if result.returncode:
            print("ERROR: {}: {}".format(filename, result.stderr.strip()))
            failures += 1
            continue
        try:
            output, _ = json.JSONDecoder().raw_decode(result.stdout)
        except json.JSONDecodeError as error:
            print("INVALID JSON: {}: {}".format(filename, error))
            failures += 1
            continue
        posting = (ROOT / "samples" / filename).read_text(encoding="utf-8")
        for category in CATEGORIES:
            actual = output[category + "_status"]
            evidence = output[category + "_evidence"]
            correct = actual == answer[category]
            grounded = (bool(evidence) and evidence in posting) if actual in ("yes", "no") else (not evidence or evidence in posting)
            mark = "PASS" if correct and grounded else "FAIL"
            print("{}: {} {}: expected {}, actual {}".format(
                mark, filename, category, answer[category], actual))
            if not correct or not grounded:
                failures += 1
                if not grounded:
                    print("  Evidence is not in the posting")
    print("Failures: {}".format(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
