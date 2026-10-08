# Career Match

[English](#english) · [한국어](#한국어) · [Workflow / 처리 흐름](docs/WORKFLOW.md) · [Development log / 진행 기록](docs/PROGRESS.md)

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
refusal alone does not rule out every other work visa. DDGS search is being
tested as the source of job URLs. The older Greenhouse-only fetch and save
commands remain as reference code and are not part of the planned search flow.
Scheduling and the website are not implemented yet. These values
describe what a posting says; they do not
establish an applicant's eligibility or guarantee an immigration outcome.

The script uses Qwen3-8B through a local Ollama server. This is inference with
an existing model; the sample files are evaluation examples, not training data.
CLI help, errors, and results are in English. Source-code docstrings and
project documentation retain English/Korean explanations.
Function parameters and returns have Python type hints. Pylance/Pyright uses
`pyrightconfig.json` to check the scripts in standard mode; Python itself does
not enforce these hints at runtime.

### Run locally

Use Python 3.11+ and Ollama with the `qwen3:8b` model. On this machine, the
project already has a `.venv`; on a fresh checkout, create one with
`python3 -m venv .venv`. The analyzer uses the Python standard library; the
optional search probe requires the packages in `requirements-search.txt`.

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

Legacy Greenhouse example (kept for reference, outside the DDGS search flow):

```bash
.venv/bin/python scripts/fetch_greenhouse_job.py --board nearform --job-id 7619114003
```

The collector saves plain text and source metadata under
`data/results/greenhouse/<board>/`; this directory is excluded from Git.
Job pages may change or disappear. Analyze a saved `.txt` file with
`scripts/analyze_job.py --file <path>` after starting Ollama.

To save the analysis together with its source URL and fetch time, then list
results by category and status:

```bash
.venv/bin/python scripts/save_job_analysis.py --board nearform --job-id 7619114003
.venv/bin/python scripts/list_job_analyses.py
.venv/bin/python scripts/list_job_analyses.py --category visa_sponsorship --status unknown
```

Saved analysis JSON goes under `data/results/analyses/<board>/`, which is also
excluded from Git. The list command accepts `yes`, `no`, and `unknown`; an
`unknown` result means the posting did not establish a clear answer.
`scripts/job_record.py` defines this saved format and validates JSON values
when they enter the save and list commands.

### Search-source probe

`scripts/probe_job_search.py` tests a possible search source. It uses DDGS's
automatic metasearch backend, removes duplicate URLs, and saves extracted page
text under ignored `data/results/search_probe/`. It does not classify visas or
confirm that a result is an active US job posting. Inspect `latest.json` and
the saved `.txt` files before using a result in the analyzer.

Check dependencies before installing missing packages, then run one small query:

```bash
.venv/bin/python -m pip show ddgs beautifulsoup4
.venv/bin/python -m pip install -r requirements-search.txt
.venv/bin/python scripts/probe_job_search.py --query 'site:jobs.lever.co "machine learning engineer" "United States"' --limit 5
```

The install command is needed only for missing packages. `text_extracted`
means at least 500 characters were extracted; it does not prove that the text
is a complete job description. This probe does not run Ollama.

### Samples and validation

The current workflow is:

1. `scripts/analyze_job.py` reads one plain-text posting and asks local Ollama
   for six classifications and source evidence.
2. `scripts/check_samples.py` runs the analyzer on every fictional posting in
   `samples/` and compares its output with `samples/expected_statuses.json`.
3. The checker reports mismatches in fictional examples so we can inspect the
   posting, expected label, prompt, and extraction logic. It does not train the
   model. The legacy Greenhouse collector is retained as an example of fetching
   a real posting; DDGS discovery is still being tested.

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

### Roadmap and Git workflow

1. Verify DDGS search results against live job pages, then connect valid postings to analysis and saving.
2. Build a website with category filters, source text, and original posting links.
3. Add resume-based recommendations after the source evidence is reliable.

The [dated development log](docs/PROGRESS.md) records decisions, failures,
fixes, and validation. After each chapter, the user reviews the change,
updates the log, and runs Git commands personally. Keep resumes, credentials,
and private analysis data out of Git. See the `.gitignore` rules.
The [workflow guide](docs/WORKFLOW.md) maps each command to its input and
output.

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
거절한다고 판단하지 않습니다. DDGS 검색을 공고 URL 수집 수단으로 시험 중입니다.
기존 Greenhouse 전용 수집·저장 명령은 참고용으로 남겨두었고 현재 검색 흐름에서는
사용하지 않습니다. 자동 실행과 웹사이트는 아직 구현하지 않았습니다. 이 값은 공고에
적힌 내용을 나타내며, 지원자의 자격이나 비자 승인 여부를 보장하지 않습니다.

스크립트는 로컬 Ollama 서버로 Qwen3-8B를 실행합니다. 기존 모델을
사용한 추론이며, 샘플 파일은 학습 데이터가 아닌 검증용 예제입니다.
명령행 도움말·오류·실행 결과는 영어로 표시합니다. 코드의 docstring과
프로젝트 문서에는 영어/한국어 설명을 유지합니다.
함수 인자와 반환값에는 Python 타입 힌트를 붙였습니다. Pylance/Pyright는
`pyrightconfig.json`에 따라 스크립트를 standard 모드로 검사합니다.
Python 실행 자체가 타입 힌트를 강제하지는 않습니다.

### 로컬 실행

Python 3.11 이상과 `qwen3:8b` 모델이 설치된 Ollama가 필요합니다.
현재 맥북에는 프로젝트 전용 `.venv`가 이미 있습니다. 새 체크아웃에서는
`python3 -m venv .venv`로 만들면 됩니다. 분석기는 Python 표준 라이브러리로
실행되며, 선택적인 검색 시험에는 `requirements-search.txt`의 패키지가 필요합니다.

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

이전 Greenhouse 예제입니다. 참고용으로 남겨두었으며 현재 DDGS 검색 흐름에서는
사용하지 않습니다. 실행할 때는 게시판 이름과 공고 ID를 입력합니다.

```bash
.venv/bin/python scripts/fetch_greenhouse_job.py --board nearform --job-id 7619114003
```

수집기는 일반 텍스트와 출처 정보를 `data/results/greenhouse/<board>/` 아래에
저장합니다. 이 폴더는 Git에서 제외합니다. 공고는 수정되거나 사라질 수 있습니다.
Ollama를 실행한 뒤 저장된 `.txt` 파일을 `scripts/analyze_job.py --file <path>`로
분석할 수 있습니다.

분석 결과를 원문 URL·수집 시각과 함께 저장하고, 항목과 상태별로 조회하려면:

```bash
.venv/bin/python scripts/save_job_analysis.py --board nearform --job-id 7619114003
.venv/bin/python scripts/list_job_analyses.py
.venv/bin/python scripts/list_job_analyses.py --category visa_sponsorship --status unknown
```

결과 JSON은 Git에서 제외되는 `data/results/analyses/<board>/`에 저장합니다.
조회 명령은 `yes`, `no`, `unknown`을 모두 허용합니다. `unknown`은 공고만으로
확실한 답을 확인하지 못했다는 뜻입니다.
`scripts/job_record.py`는 저장 형식을 정의하고 저장·조회 명령으로 들어오는
JSON 값을 검사합니다.

### 검색 수집원 시험

`scripts/probe_job_search.py`는 새 검색 방식의 작은 실험입니다. DDGS의
자동 메타검색으로 URL 후보를 찾고 중복을 제거한 뒤, 추출한 페이지 텍스트를
Git에서 제외되는 `data/results/search_probe/`에 저장합니다. 이 단계에서는
비자를 분석하거나 실제 미국 공고인지 확정하지 않습니다. `latest.json`과
저장된 `.txt` 파일을 직접 열어 원문을 확인해야 합니다.

먼저 패키지 설치 여부를 확인하고, 없는 패키지만 설치한 뒤 검색어 하나로
시험합니다.

```bash
.venv/bin/python -m pip show ddgs beautifulsoup4
.venv/bin/python -m pip install -r requirements-search.txt
.venv/bin/python scripts/probe_job_search.py --query 'site:jobs.lever.co "machine learning engineer" "United States"' --limit 5
```

설치 명령은 패키지가 없을 때만 실행하면 됩니다. `text_extracted`는 500자
이상의 텍스트를 얻었다는 뜻이며, 완전한 채용 공고인지 보장하지 않습니다.
이 시험 스크립트는 Ollama를 호출하지 않습니다.

### 샘플과 검증

현재 분석·검증 흐름은 다음과 같습니다.

1. `scripts/analyze_job.py`가 일반 텍스트 공고 한 개를 읽고 로컬 Ollama에
   여섯 항목의 판단과 원문 근거를 요청합니다.
2. `scripts/check_samples.py`가 `samples/`의 가상 공고를 하나씩 분석하고
   `samples/expected_statuses.json`의 기대값과 비교합니다.
3. 가상 예제에서 불일치가 나오면 공고 원문, 기대값, 모델 지침, 근거 추출
   코드를 확인합니다. 이 과정에서 모델을 학습시키지는 않습니다.
   이전 Greenhouse 수집기는 실제 공고 수집 예제로 남겨두었고, DDGS 검색은
   아직 시험 중입니다.

`samples/`의 파일은 모두 가상 채용 공고입니다. 여섯 항목의
기대값은 [`samples/expected_statuses.json`](samples/expected_statuses.json)에
있습니다. 샘플 검사는 모델의 여섯 항목 출력을 이 정답표와 비교합니다.
2026-10-01에 가상 공고 16개의 항목별 검사 96개가 모두 통과했고,
`yes/no` 판단의 근거도 공고 원문에서 확인했습니다.
검사를 실행해도 모델의 가중치가 바뀌거나 학습되지는 않습니다.
이는 실제 공고에서의 정확도를 입증하지 않습니다. 현재 문장 추출은
문장부호 또는 줄바꿈을 기준으로 나눕니다. HTML은 먼저 일반 텍스트로
변환해야 하며 불릿·복잡한 표현은 추가 평가가 필요합니다.

### 로드맵과 Git 작업 방식

1. DDGS 검색 결과가 실제로 열리는 공고인지 확인하고, 유효한 공고를 분석·저장 단계에 연결합니다.
2. 항목별 필터, 근거 문장, 원문 링크가 있는 웹 화면을 만듭니다.
3. 공고 근거가 신뢰할 만해지면 이력서 기반 추천을 추가합니다.

[날짜별 진행 기록](docs/PROGRESS.md)에 판단, 실패, 수정, 검증 결과를
남깁니다. 챕터가 끝나면 사용자가 변경 사항을 확인하고 Git 명령을
직접 실행합니다. 이력서·인증 정보·개인 분석 데이터는 Git에 넣지
않습니다. `.gitignore` 규칙을 참고하세요.
[처리 흐름 문서](docs/WORKFLOW.md)에서 각 명령의 입력과 출력을 볼 수 있습니다.

참고 자료: [Ollama 채팅 API](https://docs.ollama.com/api/chat),
[미 국토안보부 실무훈련 개요](https://studyinthestates.dhs.gov/assets/SEVP_PracticalTrainingOverview_1-pager.pdf),
[미 이민국 H-1B 고용주 청원 안내](https://www.uscis.gov/sites/default/files/document/forms/i-129h1instr-feerule.pdf),
[미 이민국 고용주 영주권 지원 안내](https://www.uscis.gov/sites/default/files/document/guides/E2en.pdf).
