# Career Match

[English](#english) · [한국어](#한국어) · [Development log / 진행 기록](docs/PROGRESS.md)

## English

Career Match is a prototype for finding US job postings that explicitly discuss
work authorization and employer support for international students. The planned
categories are CPT, OPT, STEM OPT, H-1B, and employment-based permanent residence.
Each result should show the source sentence used for its classification.

### Current scope

The Python script currently analyzes **OPT and STEM OPT only**. It returns
`yes`, `no`, or `unknown` for each category and the matching sentence from the
posting. CPT, H-1B, green-card support, live job collection, and a website are
future chapters. These values describe what a posting says; they do not
establish an applicant's eligibility or guarantee an immigration outcome.

The script uses Qwen3-8B through a local Ollama server. This is inference with
an existing model; the sample files are evaluation examples, not training data.

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
OPT `yes` and STEM OPT `no`.

### Samples and validation

All files in `samples/` are fictional job postings. The expected status for
each of the five planned categories is in
[`samples/expected_statuses.json`](samples/expected_statuses.json). The
current OPT/STEM OPT analyzer matched the expected statuses and source sentences
for six fictional cases, including one that mentions STEM OPT but not ordinary
OPT. This does not establish accuracy on real postings. Sentence extraction
currently splits on punctuation followed by whitespace; HTML, bullets, and
complex wording still need evaluation.

### Roadmap and Git workflow

1. Add CPT, H-1B, and employment-based permanent-residence classifications.
2. Collect real US job postings and evaluate them against human-reviewed labels.
3. Build a website with category filters, source text, and original posting links.
4. Add resume-based recommendations after the source evidence is reliable.

The [dated development log](docs/PROGRESS.md) records decisions, failures,
fixes, and validation. After each chapter, the user reviews the change,
updates the log, and runs Git commands personally. Keep resumes, credentials,
and private analysis data out of Git. See the `.gitignore` rules.

Ollama API reference: https://docs.ollama.com/api/chat

## 한국어

Career Match는 미국 유학생을 위해 채용 공고에 명시된 취업 허가 및 고용주
지원 정보를 찾는 프로젝트입니다. 예정된 항목은 CPT, OPT, STEM OPT,
H-1B, 취업 기반 영주권입니다. 각 판단에는 근거가 된 공고 원문을 표시합니다.

### 현재 범위

현재 Python 스크립트는 **OPT와 STEM OPT만** 분석합니다. 항목별로
`yes`, `no`, `unknown`과 근거 문장을 반환합니다. CPT·H-1B·영주권,
실제 공고 수집, 웹사이트는 다음 챕터에서 구현합니다. 이 값은 공고에
적힌 내용을 나타내며, 지원자의 자격이나 비자 승인 여부를 보장하지 않습니다.

스크립트는 로컬 Ollama 서버로 Qwen3-8B를 실행합니다. 기존 모델을
사용한 추론이며, 샘플 파일은 학습 데이터가 아닌 검증용 예제입니다.

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
명령행 옵션을 보여줍니다. 혼합 예제의 기대값은 OPT `yes`, STEM OPT
`no`입니다.

### 샘플과 검증

`samples/`의 파일은 모두 가상 채용 공고입니다. 앞으로 다룰 다섯 항목의
기대값은 [`samples/expected_statuses.json`](samples/expected_statuses.json)에
있습니다. 현재 분석기는 일반 OPT를 언급하지 않고 STEM OPT만 언급한
사례를 포함한 가상 공고 6개에서 기대 상태와 원문 근거를 확인했습니다.
이는 실제 공고에서의 정확도를 입증하지 않습니다. 현재 문장 추출은
문장부호 뒤 공백을 기준으로 나누므로 HTML·불릿·복잡한 표현은 추가
평가가 필요합니다.

### 로드맵과 Git 작업 방식

1. CPT·H-1B·취업 기반 영주권 분류를 추가합니다.
2. 실제 미국 공고를 수집하고 사람이 확인한 정답과 비교합니다.
3. 항목별 필터, 근거 문장, 원문 링크가 있는 웹 화면을 만듭니다.
4. 공고 근거가 신뢰할 만해지면 이력서 기반 추천을 추가합니다.

[날짜별 진행 기록](docs/PROGRESS.md)에 판단, 실패, 수정, 검증 결과를
남깁니다. 챕터가 끝나면 사용자가 변경 사항을 확인하고 Git 명령을
직접 실행합니다. 이력서·인증 정보·개인 분석 데이터는 Git에 넣지
않습니다. `.gitignore` 규칙을 참고하세요.

Ollama API 참고: https://docs.ollama.com/api/chat
