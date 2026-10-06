"""Compare sample answers with model output. / 샘플 정답과 모델 출력을 비교합니다."""

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("cpt", "opt", "stem_opt", "visa_sponsorship", "h1b", "green_card")


def main():
    expected = json.loads(
        (ROOT / "samples" / "expected_statuses.json").read_text(encoding="utf-8")
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
            str(ROOT / "scripts" / "analyze_job.py"),
            "--file",
            # execute analyze_job.py script with the --file argument
            # str = converting the Path object to a string
            # --file means the next argument is the path to the file that analyze_job.py will analyze.
            # the path is underline code.
            str(ROOT / "samples" / filename),
            # so, it's same with "python scripts/analyze_job.py --file samples/job.txt"
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=330)
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

            # A conditional expression chooses the evidence rule. / 조건식으로 근거 검사 규칙을 고릅니다.
            # JS: (actual === "yes" || actual === "no")
            #   ? Boolean(evidence) && posting.includes(evidence)
            #   : !evidence || posting.includes(evidence)

            mark = "PASS" if correct and grounded else "FAIL"
            print(
                f"{mark}: {filename} {category}: expected {answer[category]}, actual {actual}"
            )
            if not correct or not grounded:
                failures += 1
                if not grounded:
                    print("  Evidence is not in the posting")
    print(f"Failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
