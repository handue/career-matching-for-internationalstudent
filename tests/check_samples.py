"""Regression-check sample answers. / 샘플 정답으로 분석기의 변경을 검사합니다."""

import json
from pathlib import Path
import subprocess
import sys

ROOT: Path = Path(__file__).resolve().parents[1]
CATEGORIES: tuple[str, ...] = ("cpt", "opt", "stem_opt", "visa_sponsorship", "h1b", "green_card")


def main() -> int:
    expected = json.loads(
        (ROOT / "samples" / "expected_statuses.json").read_text(encoding="utf-8")
    )
    expected_evidence = json.loads(
        (ROOT / "samples" / "expected_evidence.json").read_text(encoding="utf-8")
    )
    # json.loads = turns the JSON string into a Python dictionary.
    # ex) sample JSON: {"sample1.txt": {"cpt": "yes", "opt": "no", ...}, "sample2.txt": {...}}

    sample_names = {path.name for path in (ROOT / "samples").glob("*.txt")}
    missing = sample_names - expected.keys()
    # Set difference: find sample files without answer keys. / 정답표에 없는 샘플 파일을 찾습니다.
    # ex) sample_names = {"sample1.txt", "sample2.txt", "sample3.txt"}, expected.keys() = {"sample1.txt", "sample2.txt"} => missing = {"sample3.txt"}

    if missing:
        print("Missing answer keys: {}".format(", ".join(sorted(missing))))
        return 1
    failures = 0
    for filename, answer in expected.items():
        # items() supplies each filename and its expected answers. / 파일명과 기대 답을 함께 꺼냅니다.

        command = [
            sys.executable,
            # it returns the path of the current Python interpreter executable. This is useful when you want to run a Python script using the same interpreter that is currently running your code.
            # It ensures that the script is executed in the same environment, with the same version of Python and installed packages.
            "-m", "job_pipeline.analysis.extraction",
            "--file",
            # execute the analysis module with the --file argument
            # str = converting the Path object to a string
            # --file supplies the posting path to the extraction module. / 분석 모듈에 공고 경로를 전달합니다.
            # the path is underline code.
            str(ROOT / "samples" / filename),
            # so, it's same with "python -m job_pipeline.analysis.extraction --file samples/job.txt"
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=330, cwd=ROOT)
        # subprocess = for running another program as a separate process.
        # 그냥 파이썬 실행할 프로그램 하나 더 분리해서 만드는거.
        if result.returncode != 0:
            # returncode = 0 means the command was successful, while a non-zero return code indicates an error occurred during execution.
            # In Python, 0 is considered False. / Python에서 0은 거짓으로 취급합니다.
            # So, below code means if the command was not successful, print the error message and increment the failures counter.
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
            grounded = (
                (bool(evidence) and evidence in posting)
                if actual in ("yes", "no")
                else (not evidence or evidence in posting)
            )
            # Some cases require the exact sentence, including its future-role scope.
            # 일부 사례는 향후 정규직 조건까지 담긴 정확한 근거 문장을 요구합니다.
            required_evidence = expected_evidence.get(filename, {}).get(category)
            evidence_matches = required_evidence is None or evidence == required_evidence

            # A conditional expression chooses the evidence rule. / 조건식으로 근거 검사 규칙을 고릅니다.
            # JS: (actual === "yes" || actual === "no")
            #   ? Boolean(evidence) && posting.includes(evidence)
            #   : !evidence || posting.includes(evidence)

            mark = "PASS" if correct and grounded and evidence_matches else "FAIL"
            print(
                f"{mark}: {filename} {category}: expected {answer[category]}, actual {actual}"
            )
            if not correct or not grounded or not evidence_matches:
                failures += 1
                if not grounded:
                    print("  Evidence is not in the posting")
                if not evidence_matches:
                    print(f"  Expected evidence: {required_evidence}")
    print(f"Failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
