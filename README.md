# Career Match

[English](#english) · [한국어](#한국어) · [Development log / 진행 기록](docs/PROGRESS.md)

## English

Career Match is a prototype for finding US job postings that explicitly discuss
work authorization and employer support for international students. The planned
categories are CPT, OPT, STEM OPT, work-visa sponsorship, H-1B sponsorship,
and employment-based permanent-residence sponsorship.
Each result should show the source sentence used for its classification.

### Current scope

The Python script analyzes **all six categories** above. It returns
`yes`, `no`, or `unknown` for each category and the matching sentence from the
posting. Visa sponsorship means employer support for a work visa; an H-1B
refusal alone does not rule out every other work visa. The current collector
saves one public Greenhouse posting at a time; a scheduled feed and website
are future chapters. These values describe what a posting says; they do not
establish an applicant's eligibility or guarantee an immigration outcome.

The script uses Qwen3-8B through a local Ollama server. This is inference with
an existing model; the sample files are evaluation examples, not training data.
CLI help, errors, and results are in English. Source-code docstrings and
project documentation retain English/Korean explanations.

### Run locally

Use Python 3.11+ and Ollama with the `qwen3:8b` model. On this machine, the
project already has a `.venv`; on a fresh checkout, create one with
`python3 -m venv .venv`. No third-party Python packages are needed yet.

In one terminal, start Ollama if it is not already running:

```bash
ollama serve
```

Download the model once, then run an example from another terminal:

```bash
ollama pull qwen3:8b
cd /Users/anjung/coding/career-match
.venv/bin/python scripts/analyze_job.py --file samples/visa_mixed.txt
```

Use `--dry-run` to print the input without calling the model. Use `--help` to
see the command-line options. On the mixed example, the expected statuses are
CPT `yes`, OPT `yes`, and STEM OPT `no`. Run the full fictional sample check with:

```bash
.venv/bin/python scripts/check_samples.py
```

To fetch one public Greenhouse posting, use its board token and job ID:

```bash
.venv/bin/python scripts/fetch_greenhouse_job.py --board nearform --job-id 7619114003
```

The collector saves plain text and source metadata under
`data/results/greenhouse/<board>/`; this directory is excluded from Git.
Job pages may change or disappear. Analyze a saved `.txt` file with
`scripts/analyze_job.py --file <path>` after starting Ollama.

### Samples and validation

The current workflow is:

1. `scripts/analyze_job.py` reads one plain-text posting and asks local Ollama
   for six classifications and source evidence.
2. `scripts/check_samples.py` runs the analyzer on every fictional posting in
   `samples/` and compares its output with `samples/expected_statuses.json`.
3. The checker reports mismatches so we can review the posting, expected label,
   prompt, and extraction logic. It does not train the model. The Greenhouse
   collector provides additional real postings for separate human review.

All files in `samples/` are fictional job postings. The expected status for
each of the six categories is in
[`samples/expected_statuses.json`](samples/expected_statuses.json). The
sample check compares the model's six answers with this key.
All 96 category checks across 16 fictional postings passed on 2026-10-01;
positive and negative answers also had evidence found in the posting text.
The check does not update model weights or train the model. This does not establish
accuracy on real postings. Sentence extraction
currently splits on punctuation or line breaks; HTML must be converted to
plain text first. Bullets and complex wording still need more evaluation.

The [real-posting review](docs/REAL_POSTING_REVIEW.md) checks six short excerpts
and one complete Greenhouse posting. It identified HTML conversion as a required
step for the collector added afterward.

### Roadmap and Git workflow

1. Expand real US posting collection and evaluate against human-reviewed labels.
2. Build a website with category filters, source text, and original posting links.
3. Add resume-based recommendations after the source evidence is reliable.

The [dated development log](docs/PROGRESS.md) records decisions, failures,
fixes, and validation. After each chapter, the user reviews the change,
updates the log, and runs Git commands personally. Keep resumes, credentials,
and private analysis data out of Git. See the `.gitignore` rules.

References: [Ollama chat API](https://docs.ollama.com/api/chat),
[DHS practical-training overview](https://studyinthestates.dhs.gov/assets/SEVP_PracticalTrainingOverview_1-pager.pdf),
[USCIS H-1B employer petition](https://www.uscis.gov/sites/default/files/document/forms/i-129h1instr-feerule.pdf),
[USCIS employer-sponsored permanent residence](https://www.uscis.gov/sites/default/files/document/guides/E2en.pdf).

## 한국어

Career Match는 미국 유학생을 위해 채용 공고에 명시된 취업 허가 및 고용주
지원 정보를 찾는 프로젝트입니다. 분석 항목은 CPT, OPT, STEM OPT,
취업 비자 스폰서십, H-1B 스폰서십, 취업 기반 영주권 스폰서십입니다.
각 판단에는 근거가 된 공고 원문을 표시합니다.

### 현재 범위

현재 Python 스크립트는 **위의 여섯 항목**을 분석합니다. 항목별로
`yes`, `no`, `unknown`과 근거 문장을 반환합니다. 비자 스폰서십은
고용주의 취업 비자 지원을 뜻합니다. H-1B 거절만으로 다른 모든 취업 비자도
거절한다고 판단하지 않습니다. 현재 수집기는 공개 Greenhouse 공고를 한 번에
하나씩 저장합니다. 정기 수집과 웹사이트는 다음 챕터에서 구현합니다. 이 값은 공고에
적힌 내용을 나타내며, 지원자의 자격이나 비자 승인 여부를 보장하지 않습니다.

스크립트는 로컬 Ollama 서버로 Qwen3-8B를 실행합니다. 기존 모델을
사용한 추론이며, 샘플 파일은 학습 데이터가 아닌 검증용 예제입니다.
명령행 도움말·오류·실행 결과는 영어로 표시합니다. 코드의 docstring과
프로젝트 문서에는 영어/한국어 설명을 유지합니다.

### 로컬 실행

Python 3.11 이상과 `qwen3:8b` 모델이 설치된 Ollama가 필요합니다.
현재 맥북에는 프로젝트 전용 `.venv`가 이미 있습니다. 새 체크아웃에서는
`python3 -m venv .venv`로 만들면 됩니다. 아직 외부 Python 패키지는
필요하지 않습니다.

Ollama가 실행 중이 아니라면 터미널 하나에서 서버를 켭니다.

```bash
ollama serve
```

모델을 한 번 다운로드한 뒤 다른 터미널에서 예제를 실행합니다.

```bash
ollama pull qwen3:8b
cd /Users/anjung/coding/career-match
.venv/bin/python scripts/analyze_job.py --file samples/visa_mixed.txt
```

`--dry-run`은 모델을 호출하지 않고 입력만 출력합니다. `--help`는
명령행 옵션을 보여줍니다. 혼합 예제의 기대값은 CPT `yes`, OPT `yes`,
STEM OPT `no`입니다. 가상 샘플 전체를 검사하려면 다음을 실행합니다.

```bash
.venv/bin/python scripts/check_samples.py
```

공개 Greenhouse 공고 하나를 가져올 때는 게시판 이름과 공고 ID를 입력합니다.

```bash
.venv/bin/python scripts/fetch_greenhouse_job.py --board nearform --job-id 7619114003
```

수집기는 일반 텍스트와 출처 정보를 `data/results/greenhouse/<board>/` 아래에
저장합니다. 이 폴더는 Git에서 제외합니다. 공고는 수정되거나 사라질 수 있습니다.
Ollama를 실행한 뒤 저장된 `.txt` 파일을 `scripts/analyze_job.py --file <path>`로
분석할 수 있습니다.

### 샘플과 검증

현재 분석·검증 흐름은 다음과 같습니다.

1. `scripts/analyze_job.py`가 일반 텍스트 공고 한 개를 읽고 로컬 Ollama에
   여섯 항목의 판단과 원문 근거를 요청합니다.
2. `scripts/check_samples.py`가 `samples/`의 가상 공고를 하나씩 분석하고
   `samples/expected_statuses.json`의 기대값과 비교합니다.
3. 불일치가 나오면 공고 원문, 기대값, 모델 지침, 근거 추출 코드를
   검토합니다. 이 과정에서 모델을 학습시키지는 않습니다. Greenhouse 수집기는
   별도로 사람이 검토할 실제 공고를 제공합니다.

`samples/`의 파일은 모두 가상 채용 공고입니다. 여섯 항목의
기대값은 [`samples/expected_statuses.json`](samples/expected_statuses.json)에
있습니다. 샘플 검사는 모델의 여섯 항목 출력을 이 정답표와 비교합니다.
2026-10-01에 가상 공고 16개의 항목별 검사 96개가 모두 통과했고,
`yes/no` 판단의 근거도 공고 원문에서 확인했습니다.
검사를 실행해도 모델의 가중치가 바뀌거나 학습되지는 않습니다.
이는 실제 공고에서의 정확도를 입증하지 않습니다. 현재 문장 추출은
문장부호 또는 줄바꿈을 기준으로 나눕니다. HTML은 먼저 일반 텍스트로
변환해야 하며 불릿·복잡한 표현은 추가 평가가 필요합니다.

[실제 공고 검토](docs/REAL_POSTING_REVIEW.md)에서는 짧은 발췌 여섯 개와
Greenhouse 전체 공고 한 개를 확인했습니다. 이후 추가한 수집기에
HTML 변환 단계가 필요하다는 점을 확인했습니다.

### 로드맵과 Git 작업 방식

1. 실제 미국 공고 수집을 확대하고 사람이 확인한 정답과 비교합니다.
2. 항목별 필터, 근거 문장, 원문 링크가 있는 웹 화면을 만듭니다.
3. 공고 근거가 신뢰할 만해지면 이력서 기반 추천을 추가합니다.

[날짜별 진행 기록](docs/PROGRESS.md)에 판단, 실패, 수정, 검증 결과를
남깁니다. 챕터가 끝나면 사용자가 변경 사항을 확인하고 Git 명령을
직접 실행합니다. 이력서·인증 정보·개인 분석 데이터는 Git에 넣지
않습니다. `.gitignore` 규칙을 참고하세요.

참고 자료: [Ollama 채팅 API](https://docs.ollama.com/api/chat),
[미 국토안보부 실무훈련 개요](https://studyinthestates.dhs.gov/assets/SEVP_PracticalTrainingOverview_1-pager.pdf),
[미 이민국 H-1B 고용주 청원 안내](https://www.uscis.gov/sites/default/files/document/forms/i-129h1instr-feerule.pdf),
[미 이민국 고용주 영주권 지원 안내](https://www.uscis.gov/sites/default/files/document/guides/E2en.pdf).
