# Development Log / 진행 기록

This document records the order of work, decisions, failures, fixes, and
validation by date. Entries before 2026-10-01 summarize work completed on
those dates; the first Git commit was created on 2026-10-01. Earlier Git
commits were not fabricated. The user runs Git commands personally.

이 문서는 작업 순서, 판단, 실패, 수정, 검증을 날짜별로 기록합니다.
2026-10-01 이전 항목은 해당 날짜의 작업을 정리한 것입니다. 첫 Git
커밋은 2026-10-01에 생성했으며 과거 커밋을 임의로 만들지 않았습니다.
Git 명령은 사용자가 직접 실행합니다.

## English

### 2026-09-28 — Project setup

- Created the personal US job-posting analysis project and Python environment.
- Installed Ollama and Qwen3-8B; extracted JSON from one fictional posting.
- The model initially marked an explicit sponsorship refusal as `unknown`.
  After revising the instructions, the example returned `no` with source text.

### 2026-09-29 — More classification examples

- Added fictional postings with positive, negative, conditional, and absent
  sponsorship language.
- Found that the model confused a degree requirement with experience and
  adjusted the instructions.
- Later removed the broad `sponsorship` field to classify each program
  independently.

### 2026-09-30 — Separate OPT classification

- Set the planned categories to CPT, OPT, STEM OPT, H-1B, and
  employment-based permanent residence.
- Added separate OPT status and source-evidence fields.
- Found that generic sponsorship refusal and STEM OPT language were being
  mistaken for ordinary OPT decisions.
- Limited OPT decisions to sentences that directly mention ordinary OPT.
- Checked positive, negative, unknown, and mixed fictional examples.

### 2026-10-01 — Six-category analyzer and validation

- Added fictional postings covering all five categories and
  `samples/expected_statuses.json` as an evaluation key, not training data.
- Found that the model sometimes paraphrased evidence; the code now copies
  the selected sentence from the original posting.
- Added STEM OPT status and evidence separately from ordinary OPT.
- Checked the expected states and source sentences on six fictional postings.
- Created the initial Git commit and this dated log. GitHub publishing is
  performed by the user.
- Added parallel English/Korean documentation, docstrings, and CLI messages.
- Added CPT classification with separate status and verbatim source evidence.
  Added a CPT-only fictional posting to check that OPT remains `unknown`.
- Added `scripts/check_samples.py` to compare model output with the answer key.
  Running this check does not train or fine-tune the model.
- All 21 CPT/OPT/STEM OPT checks across seven fictional postings passed.
- Added separate work-visa sponsorship, H-1B sponsorship, and employment-based
  green-card sponsorship statuses with verbatim evidence.
- Added cases for a general visa refusal with OPT acceptance, a general visa
  offer without named H-1B support, H-1B refusal without a general visa
  refusal, conditional visa support, and green-card support/refusal.
- The first six-category check exposed overgeneralization from H-1B refusal
  and a missed conditional offer. Refined the source-sentence filter and model
  instructions, then corrected two answer-key entries against their text.
- Added answer-key entries for two older sample postings and a coverage check
  that reports any future sample without an answer key.
- Final check: all 96 category results across 16 fictional postings passed;
  `yes`/`no` evidence was present in the source text.
- Reviewed six short excerpts from current employer pages and one complete
  Greenhouse posting. Applicant questions and E-Verify alone stayed `unknown`.
- Found that the Greenhouse API returns escaped HTML; unescape and convert it
  before analysis. Splitting on line breaks now keeps evidence sentences clean.
- A visa-transfer/new-H-1B-CAP example exposed mixed support. The classifier
  now leaves the broad H-1B status `unknown` rather than a blanket `no`.
- Re-ran all 96 fictional category checks after these changes: zero failures.
  Syntax, CLI help, dry-run, and line-based sentence splitting also passed.
- Switched all CLI help, errors, and printed results to English while keeping
  bilingual source-code docstrings and project documentation.
- Remaining gaps: no real job collection or website. Complex HTML and bullet
  formatting still need evaluation.

At this checkpoint, the project consists of the analyzer, sample checker, 16
fictional postings, their answer key, and README. The 96/96 result is a
fictional-sample check, not a measured accuracy rate on live job postings.

### 2026-10-02 — First Greenhouse collector

- Added `scripts/fetch_greenhouse_job.py` to retrieve one public posting by
  board token and job ID, convert escaped HTML to plain text, and save source
  metadata alongside the posting.
- The collector writes under ignored `data/results/greenhouse/`; it does not
  run on a schedule or build an accuracy dataset.
- Checked syntax, CLI help, HTML conversion, and one public Nearform fetch.
  The follow-up analyzer run could not reach the local Ollama server.

### 2026-10-05 — Code walkthrough and documentation

- Reviewed the sample checker and Greenhouse collector step by step, including
  subprocess exit codes, evidence checks, argument parsing, HTML cleanup, and
  output paths.
- Clarified comments, made the checker's failure condition explicit, and used
  f-strings for its status output. Documented how to run the collector.
- Added type hints to all script functions and the HTML parser state, described
  the heterogeneous output schema with `TypedDict`, and enabled standard
  Pylance/Pyright checks for `scripts/`.

### 2026-10-06 — Saved analyses and status filtering

- Added a command that runs the analyzer on an already fetched Greenhouse
  posting and saves its result with the original URL and fetch time.
- Added a separate command to list saved analyses and filter any of the six
  categories by `yes`, `no`, or `unknown`. Unknown results remain visible.
- The first real posting previously returned visa sponsorship `no` with an
  exact source sentence; its other five categories were `unknown`. The CLI
  filter is an inspection tool, not yet a website or scheduled collector.
- Defined the saved source and analysis objects with `TypedDict` and checked
  the actual JSON values before treating them as typed records. The save and
  list commands now share this validation in `scripts/job_record.py`.
- Documented the four-stage fetch, analyze, save, and list workflow. Syntax
  compilation of the new scripts passed when run by the user.

### 2026-10-06 — Workflow scope

- A Latitude AI fetch attempt returned HTTP 404 from the Greenhouse Job Board
  API. No posting or analysis was saved from that attempt.
- Removed the proposed manual real-posting review chapter. The current product
  flow is fetch, analyze, save, and list. Fictional sample checks remain as
  code regression checks.

### 2026-10-08 — Search-source probe

- Added an isolated DDGS metasearch probe that searches one query, removes
  duplicate URLs, fetches HTML, and stores extracted text for inspection.
- Kept visa analysis and ranking outside this probe. Extracted text alone does
  not confirm that a result is an active US job posting.
- Documented optional search dependencies and commands for the user to run.
  The user ran a Lever-site query: DDGS returned three search results, but
  all three pages returned HTTP 404, so no job text was extracted. Search
  snippets alone are not usable as job postings.
- Removed the unused Greenhouse board-sync prototype and its board configuration
  while retaining single-posting fetch, analysis, and saved-result tools.
- Search queries are currently entered manually. The planned Ollama step that
  generates queries from a profile and preferences has not been implemented.
- Added a search-result bridge that saves Ollama analyses with their original
  URLs. The probe now records page-check time and JobPosting JSON-LD dates when
  present, and keeps application-form questions in extracted text. A missing
  deadline or merely accessible page does not establish that applications are open.
  The user ran the bridge on a ZipRecruiter new-grad posting. One search
  analysis was saved and listed successfully; all six visa categories were
  `unknown`, and the deadline was unavailable.
- Moved the Greenhouse-only fetch and save commands into
  `scripts/legacy_greenhouse/`. The active sample checker moved to `tests/`;
  the analyzer, search bridge, shared record validator, and list command remain
  in `scripts/`.
- Added root `main.py` to call search, analysis/save, and listing in one run.
  The individual commands still work. The query remains a manual CLI input;
  the user has not run the new entry point yet.
- Added a fictional future-sponsorship/CPT/OPT refusal example. The checker now
  requires exact evidence for this scope-sensitive case. Broadened only the
  candidate-sentence search; Ollama still decides the status. The user has not
  run this new example yet.

### 2026-10-09 — Public ATS collection (implementation pending user validation)

- Added company-board collection adapters for Greenhouse, Lever, Ashby, and
  SmartRecruiters, with explicit US-location filtering and a shared report
  format for the existing Ollama analyzer.
- Made ATS collection the default `main.py` source. DDGS remains available via
  `--source ddgs --query ...` to discover new companies or postings.
- Initial configuration contains one previously inspected Greenhouse board.
  The user has not yet run the new collector or end-to-end command.
- Added bounded DDGS board discovery with public-API validation. Verified
  boards are stored outside Git and merged with manual boards. Collection now
  rotates across boards so the first company cannot fill the entire limit.
- Moved hard-coded discovery queries to an editable JSON file and diversified
  role terms. Profile-based Ollama query generation remains unimplemented.
- UCI Handshake offers student work-authorization filters, but Handshake limits
  API access to Career Services partners; no student-account API integration
  was added. The new discovery path has not been run by the user yet.

### 2026-10-11 — Django web and database worker (awaiting user validation)

- Renamed the Django settings package to `web_config` to distinguish it from
  the project folder. Updated entry points, routing, type-checker configuration,
  and documentation; normalized active scripts' shared imports to `scripts.job_record`.

- Added a Django 5.2 LTS project, authenticated dashboard, classification
  filters, source evidence, original links, and SQLite-backed analyses.
- Added a validated collection POST endpoint returning HTTP 202 and a task ID;
  users can inspect their own queued/running/completed/failed tasks.
- Added a separate management-command worker that runs the existing ATS/Ollama
  CLI. API retry waits occur in this worker, outside web request handling.
- Added an existing-analysis importer, initial migrations, and offline Django
  tests for queueing, authentication/CSRF, ownership, filtering, and worker outcomes.
- One local worker processes the persistent database queue. The worker uses a
  file lock, logs each run, and marks interrupted jobs failed on restart.
  The standalone CLI background launcher remains a separate local tool.
- Updated setup and workflow documentation. No dependency installation,
  migration, test, server, or live collection was executed by the assistant;
  runtime validation remains for the user.

### 2026-10-11 — Pipeline package refactor (pending user execution)

- Moved active `scripts/` logic into `job_pipeline/`, grouped by discovery,
  ATS collection, optional page search, and AI analysis. Shared record validation,
  project paths, and saved-result listing have dedicated modules.
- Split CLI argument handling from `run_pipeline`; `main.py` is now a thin entry.
  Django's worker executes the package CLI in a separate child process, retaining
  its 30-minute timeout, log, and nonblocking web request behavior.
- Posting analysis now directly calls typed `analyze_posting`, without launching
  a second Python CLI or decoding console output.
- Removed unused legacy Greenhouse commands and standalone background launcher.
  Preserved regression samples, existing results, migrations, and teaching comments.
- Updated imports, Pylance scope, sample checker, README, workflow, and architecture.
  Added offline pipeline wiring checks and updated the worker command assertion.
- Fixed zero-result collection reporting success when ATS boards failed.
  No DB model changes; no installs, project commands, or tests were run by the assistant.
  Historical paths below describe earlier work, not current executable commands.

### 2026-10-11 — Second structure audit (pending user execution)

- Simplified single-module collection/search folders to Python files.
- Shared board configuration validation, default paths, and CLI/pipeline option rules.
- Updated imports, documented commands, and offline regression checks.
- Recorded production gaps: shared run files, historical-result reimport, local
  locking, and development settings. The project is not yet production-validated.
- No package installations, runtime commands, or tests were run by the assistant.

### 2026-10-11 — Refactor history split (replacement pending)

- Confirmed the user committed and pushed `40ad570`, combining 58 changed files.
- Recorded a six-commit replacement plan in `WORKFLOW.md`, separating reusable
  analysis/search, ATS collection, board discovery, orchestration, Django, and docs.
- Preserve the original commit on a backup branch and keep working files during reset.
  Only the user executes reset, commits, and the lease-protected replacement push.
- Resume study at `collection.py::retry_after_seconds()` after the split is complete.

### Next chapters

0. Replace the combined refactor commit with the module/function groups recorded
   in `WORKFLOW.md`, then resume code study at
   `job_pipeline/collection.py::retry_after_seconds()`. Continue with
   `json_get()` to trace HTTP 429 → Retry-After/backoff → `time.sleep(delay)` → retry.
   This checkpoint concerns ATS API retries, not the worker's idle polling wait.
   `main.py` and `manage.py` remain separate entry points; a Django-only collection
   command has been discussed but not implemented. Git commands are run by the user;
   the replacement commits are not recorded as completed until confirmed.
1. Run the refactor's offline checks and Django checks, then validate ATS API collection with live boards. Inspect results with explicit visa language and improve date and
   availability checks before ranking candidates.
2. Review Ollama-generated ATS discovery queries and results, then connect
   profile-based query planning to the optional direct-DDGS posting search.
3. Validate the Django interface and worker, then add scheduling and production configuration.
4. Add resume-based matching once source classification is reliable.

## 한국어

### 2026-09-28 — 프로젝트 시작

- 개인용 미국 채용 공고 분석 프로젝트와 Python 가상환경을 만들었습니다.
- Ollama와 Qwen3-8B를 설치하고 가상 공고 한 개에서 JSON을 추출했습니다.
- 처음에는 명시적인 비자 스폰서십 불가를 `unknown`으로 잘못 분류했습니다.
  지침을 수정한 뒤 예제에서 `no`와 원문 근거를 확인했습니다.

### 2026-09-29 — 분류 예제 확장

- 스폰서십 가능·불가·조건부·무언급 가상 공고를 추가했습니다.
- 모델이 학위 조건을 경력으로 혼동하는 문제를 찾아 지침을 조정했습니다.
- 제도별로 독립된 판단을 위해 포괄적인 `sponsorship` 필드를 나중에
  제거했습니다.

### 2026-09-30 — OPT 독립 분류

- 예정된 항목을 CPT, OPT, STEM OPT, H-1B, 취업 기반 영주권으로 정했습니다.
- OPT 상태와 원문 근거를 별도 필드로 추가했습니다.
- 일반적인 스폰서십 불가와 STEM OPT 문구를 일반 OPT 판단으로 오해하는
  문제를 발견했습니다.
- 일반 OPT를 직접 언급한 문장으로 OPT 판단을 제한했습니다.
- 긍정·부정·무언급·혼합 가상 예제를 확인했습니다.

### 2026-10-01 — 여섯 항목 분석기와 검증

- 다섯 항목을 다루는 가상 공고와 검증용
  `samples/expected_statuses.json` 정답표를 만들었습니다.
- 모델이 근거를 바꾸어 쓰는 사례를 발견해 코드가 공고 원문 문장을
  가져오도록 수정했습니다.
- 일반 OPT와 별도로 STEM OPT 상태와 근거를 추가했습니다.
- 가상 공고 6개에서 기대 상태와 원문 근거를 확인했습니다.
- 첫 Git 커밋과 날짜별 진행 기록을 만들었습니다. GitHub 업로드는
  사용자가 직접 진행합니다.
- README·진행 기록·코드 설명·CLI 메시지를 한글/영어로 병기했습니다.
- CPT 상태와 공고 원문 근거를 별도 필드로 추가했습니다. CPT만 언급한
  가상 공고를 만들어 OPT가 `unknown`으로 남는지 확인합니다.
- `scripts/check_samples.py`를 추가해 모델 출력과 정답표를 비교합니다.
  이 검사는 모델을 학습하거나 파인튜닝하지 않습니다.
- 가상 공고 7개의 CPT·OPT·STEM OPT 검사 21개가 모두 통과했습니다.
- 취업 비자 스폰서십·H-1B·취업 기반 영주권 지원 상태와 원문 근거를
  별도로 추가했습니다.
- OPT 허용과 비자 지원 거절이 함께 있는 사례, H-1B만 거절한 사례,
  조건부 비자 지원, 영주권 지원·거절 사례를 추가했습니다.
- 첫 여섯 항목 검사에서 H-1B 거절을 전체 비자 거절로 확대하거나 조건부
  지원을 놓치는 문제를 발견했습니다. 근거 문장 추출과 모델 지침을
  수정하고, 공고 내용에 맞춰 정답표 두 항목을 바로잡았습니다.
- 기존 샘플 공고 두 개를 정답표에 더하고, 향후 정답표에서 누락된 샘플이
  있으면 검사 스크립트가 알려주도록 했습니다.
- 최종 검사에서 가상 공고 16개의 여섯 항목 판단 96개가 모두 통과했고,
  `yes/no` 근거도 공고 원문에서 확인했습니다.
- 실제 기업 페이지의 짧은 발췌 여섯 개와 Greenhouse 전체 공고 한 개를
  검토했습니다. 지원서 질문이나 E-Verify 문구만으로는 `unknown`을 유지했습니다.
- Greenhouse API가 이스케이프된 HTML을 반환하는 것을 발견했습니다.
  분석 전 HTML을 변환해야 합니다. 문장 추출은 이제 줄바꿈도 분리합니다.
- 비자 이전은 지원하지만 신규 H-1B CAP 청원은 거절하는 사례에서는
  H-1B 전체를 `no`로 단정하지 않고 `unknown`으로 남기도록 했습니다.
- 수정 후 가상 샘플 판단 96개를 다시 실행해 실패 0개를 확인했습니다.
  문법·명령행 도움말·입력 확인·줄 단위 문장 분리도 통과했습니다.
- 명령행 도움말·오류·출력은 영어로 바꾸고, 코드 docstring과 프로젝트
  문서의 한글/영어 설명은 유지했습니다.
- 남은 범위: 실제 공고 수집과 웹 화면은 미구현.
  복잡한 HTML과 불릿 형식도 추가 평가가 필요합니다.

이 시점에 만든 것은 분석기, 샘플 검사기, 가상 공고 16개와
정답표, README입니다. 96/96 통과는 가상 샘플
검사 결과이며 실제 공고에 대한 정확도 수치는 아닙니다.

### 2026-10-02 — 첫 Greenhouse 수집기

- `scripts/fetch_greenhouse_job.py`를 추가해 게시판 이름과 공고 ID로 공개
  공고 하나를 가져오고, 이스케이프된 HTML을 일반 텍스트로 변환하며,
  원문 출처 정보를 함께 저장합니다.
- 저장 위치는 Git에서 제외한 `data/results/greenhouse/`입니다. 정기
  수집이나 정확도 평가용 데이터셋은 아직 구현하지 않았습니다.
- 문법, 명령행 도움말, HTML 변환, 공개 Nearform 공고 한 건의 수집을
  확인했습니다. 이후 분석기 실행은 로컬 Ollama 연결에 실패했습니다.

### 2026-10-05 — 코드 학습과 문서 정리

- 샘플 검사기와 Greenhouse 수집기를 순서대로 읽으며 하위 프로세스 종료
  코드, 근거 검사, 명령행 입력, HTML 정리, 저장 경로를 살펴봤습니다.
- 주석을 바로잡고 샘플 검사기의 실패 조건을 명시적으로 바꿨으며,
  출력에 f-string을 사용했습니다. 수집기 실행 방법도 문서화했습니다.
- 모든 스크립트 함수와 HTML 파서 상태에 타입 힌트를 붙이고, 여러 값 형태가
  섞인 출력 스키마를 `TypedDict`로 표현했습니다. `scripts/`에 Pylance/Pyright
  standard 검사를 설정했습니다.

### 2026-10-06 — 분석 결과 저장과 상태별 조회

- 이미 수집한 Greenhouse 공고를 분석하고 원문 URL·수집 시각과 결과를
  함께 저장하는 명령을 추가했습니다.
- 여섯 항목 각각에 대해 `yes`, `no`, `unknown`으로 저장 결과를 조회하는
  명령을 추가했습니다. `unknown`도 조회할 수 있습니다.
- 앞서 실행한 실제 공고 한 건은 비자 스폰서십 `no`와 원문 근거가 나왔고,
  나머지 다섯 항목은 `unknown`이었습니다. 현재 조회 기능은 명령행 도구이며
  웹사이트나 정기 수집기는 아직 아닙니다.
- 저장된 출처·분석 객체를 `TypedDict`로 정의하고, JSON 값을 타입으로
  사용하기 전에 실제 값을 검증하도록 했습니다. 저장·조회 명령이
  `scripts/job_record.py`의 같은 검증 코드를 사용합니다.
- 수집·분석·저장·조회 네 단계를 문서화했습니다. 새 스크립트의 문법 검사는
  사용자가 직접 실행해 통과했습니다.

### 2026-10-06 — 작업 범위 정리

- Latitude AI 공고 수집 시 Greenhouse Job Board API에서 HTTP 404가
  나왔습니다. 이 시도에서는 공고나 분석 결과를 저장하지 않았습니다.
- 제안했던 실제 공고 사람 검토 챕터를 제거했습니다. 현재 제품 흐름은
  수집·분석·저장·조회입니다. 가상 샘플 검사는 코드 변경 확인용으로 유지합니다.

### 2026-10-08 — 검색 수집원 시험

- DDGS 자동 메타검색으로 검색어 하나의 URL 후보를 찾고 중복을 제거한 뒤,
  HTML 텍스트를 저장하는 독립 시험 스크립트를 추가했습니다.
- 이 단계에서는 비자 분석과 순위 계산을 연결하지 않았습니다. 텍스트를
  추출했다는 사실만으로 실제 미국 채용 공고임이 확인되지는 않습니다.
- 선택적 패키지와 사용자가 실행할 명령을 문서화했습니다.
- 사용자가 Lever 사이트 검색을 실행한 결과, 검색 결과 3개가 나왔지만 페이지는
  모두 HTTP 404를 반환해 공고 본문을 추출하지 못했습니다. 검색 요약만으로는
  공고를 분석할 수 없습니다.
- 사용하지 않는 Greenhouse 게시판 동기화 시험 코드와 설정을 제거하고,
  단일 공고 수집·분석·결과 저장 및 조회 도구는 유지했습니다.
- 지금은 검색어를 직접 입력합니다. 프로필·희망 조건을 바탕으로 Ollama가
  검색어를 만드는 단계는 아직 구현하지 않았습니다.
- 검색 결과의 원문 URL과 Ollama 분석을 함께 저장하는 연결 명령을 추가했습니다.
  검색 실험은 페이지 확인 시각과 공개된 JobPosting JSON-LD 날짜를 기록하며,
  지원 양식의 질문도 본문에서 보존합니다. 마감일이 없거나 페이지가 열리는
  것만으로 현재 접수 중이라고 확정하지 않습니다. 사용자가 ZipRecruiter 신입
  공고를 실행해 검색 분석 한 건의 저장·조회를 확인했습니다. 비자 여섯 항목과
  마감일은 모두 `unknown`이었습니다.
- Greenhouse 전용 수집·저장 명령은 `scripts/legacy_greenhouse/`로 옮겼습니다.
  계속 사용하는 샘플 검사기는 `tests/`로 옮겼습니다. 실제 분석기, 검색 결과
  연결 명령, 공통 저장 형식 검증기와 조회 명령은 `scripts/`에 남겼습니다.
- 프로젝트 루트에 `main.py`를 추가해 검색, 분석·저장, 조회를 한 번에 실행하도록
  했습니다. 개별 명령도 그대로 사용할 수 있습니다. 검색어는 아직 수동 입력이고,
  사용자가 새 진입점을 실행해 확인하기 전입니다.
- 향후 스폰서십과 CPT·OPT 거절을 함께 적은 가상 공고를 추가했습니다. 조건의
  적용 시점이 중요한 이 사례에서는 검사기가 정확한 근거 문장도 요구합니다.
  관련 문장을 모델에 전달하는 범위만 넓혔고 최종 상태는 Ollama가 판단합니다.
  새 예제는 아직 사용자가 실행해 확인하기 전입니다.

### 2026-10-09 — 공개 ATS 수집 (사용자 실행 확인 전)

- Greenhouse, Lever, Ashby, SmartRecruiters의 회사별 공개 공고 수집기를
  추가했습니다. 미국 지역이라는 명시적 근거가 있는 공고를 기존 Ollama 분석기가
  읽을 수 있는 보고서 형식으로 저장합니다.
- `main.py`의 기본 수집원을 ATS API로 바꾸고, DDGS는 새 회사·공고를 찾을 때
  `--source ddgs --query ...`로 사용할 수 있게 남겼습니다.
- 초기 설정에는 이전에 확인한 Greenhouse 게시판 하나만 넣었습니다. 새 수집기와
  전체 실행 명령은 아직 사용자가 실행해 확인하기 전입니다.
- DDGS로 ATS 게시판을 제한된 수만큼 찾고, 공개 API에서 미국 공고를 확인한 뒤
  Git 제외 목록에 저장하도록 했습니다. 수집 시 수동 목록과 합치고, 첫 회사의
  공고만 담기지 않도록 게시판별로 번갈아 선택합니다.
- 고정 검색어를 수정 가능한 JSON 파일로 옮기고 직무·경력 단계 표현을 넓혔습니다.
  프로필 기반 Ollama 검색어 생성은 아직 구현하지 않았습니다.
- UCI Handshake에는 학생용 취업 허가 필터가 있지만, Handshake API 접근은
  Career Services 파트너에게 제한됩니다. 학생 계정 API 연동은 추가하지 않았고,
  새 발견 기능은 아직 사용자가 실행해 확인하기 전입니다.

### 2026-10-11 — Django 웹과 DB 작업자 (사용자 실행 확인 전)

- 프로젝트 전체와 구분하기 위해 Django 설정 패키지를 `web_config`로 바꾸고
  진입점·라우팅·타입 검사 설정·문서를 함께 수정했습니다. 현재 사용하는 스크립트의
  공통 타입 import도 `scripts.job_record`로 맞췄습니다.

- Django 5.2 LTS 프로젝트와 로그인·분류 필터·근거 문장·원문 링크를 보여주는
  화면을 추가하고 기존 분석을 SQLite에 저장하도록 연결했습니다.
- 수집 요청은 검증 후 DB에 등록하고 HTTP 202와 작업 ID를 즉시 반환합니다.
  로그인한 사용자는 자신의 대기·실행·완료·실패 상태를 조회합니다.
- 별도 Django 관리 명령 작업자가 기존 ATS·Ollama CLI를 실행합니다.
  API 재시도 대기는 웹 요청 밖의 작업자에서 진행됩니다.
- 기존 분석 가져오기 명령·초기 마이그레이션·네트워크 없는 Django 검사를
  추가했습니다. 검사는 작업 등록·로그인/CSRF·소유권·필터·작업 결과를 다룹니다.
- DB 작업 큐를 로컬 작업자 하나가 처리하며 파일 잠금·개별 로그를 사용합니다.
  재시작 시 중단된 작업은 실패 처리합니다. 독립 CLI 백그라운드 기능은 별도 도구입니다.
- 실행 안내·처리 흐름 문서를 갱신했습니다. 설치·마이그레이션·테스트·서버·
  실제 수집은 도우미가 실행하지 않았으며 사용자의 실행 확인이 남아 있습니다.

### 2026-10-11 — 처리 모듈 리팩토링 (사용자 실행 확인 전)

- 사용 중인 `scripts/` 로직을 `job_pipeline/`로 옮겨 게시판 발견·ATS 수집·
  보조 페이지 검색·AI 분석으로 묶었습니다. 공통 타입·경로·저장 결과 조회도 분리했습니다.
- CLI 옵션과 `run_pipeline`을 분리하고 `main.py`는 얇은 진입점으로 정리했습니다.
  Django 작업자는 패키지 CLI를 자식 프로세스로 실행해 로그·30분 제한을 유지합니다.
- 공고별 분석은 타입이 있는 `analyze_posting` 직접 호출로 바꿔 별도 Python 실행과
  콘솔 출력 JSON 재해석을 제거했습니다.
- 미사용 이전 Greenhouse 명령·독립 백그라운드 실행기를 제거했습니다.
  회귀 샘플·기존 결과·마이그레이션·학습 주석은 유지했습니다.
- import·타입 검사 범위·샘플 검사·README·흐름·구조 문서를 갱신했습니다.
  네트워크 없는 처리 흐름 검사와 작업자 명령 연결 검사를 추가했습니다.
- ATS 실패가 있는데 수집 0건을 성공 처리하던 경로를 수정했습니다.
  DB 모델 변경은 없으며 설치·프로젝트 명령·테스트 실행은 사용자의 확인이 남아 있습니다.
  이전 날짜에 남은 경로는 당시 작업 기록이며 현재 실행 명령이 아닙니다.

### 2026-10-11 — 구조 재점검 (사용자 실행 확인 전)

- 파일 하나뿐인 수집·검색 폴더를 Python 모듈로 단순화했습니다.
- 게시판 설정 검증·기본 경로·CLI와 처리 함수의 옵션 검사 구현을 통합했습니다.
- import·실행 안내·네트워크 없는 회귀 검사를 갱신했습니다.
- 공통 결과 경로·과거 분석 전체 가져오기·로컬 잠금·개발 설정 등 운영 준비가
  남은 부분을 구조 문서에 명시했습니다. 아직 운영 검증이 완료된 상태가 아닙니다.
- 설치·프로그램·테스트 실행은 도우미가 진행하지 않았습니다.

### 2026-10-11 — 리팩토링 이력 분리 (교체 실행 전)

- 사용자가 변경 파일 58개를 묶은 `40ad570`을 커밋·push한 상태를 확인했습니다.
- 분석·검색, ATS 수집, 게시판 발견, 전체 흐름, Django, 문서의 여섯 커밋으로
  나누는 계획을 `WORKFLOW.md`에 기록했습니다.
- 기존 커밋은 백업 브랜치에 보존하고 reset 시 작업 파일을 유지합니다.
  reset·재커밋·lease로 보호한 교체 push는 사용자가 직접 실행합니다.
- 분리 완료 후 `collection.py::retry_after_seconds()`에서 공부를 재개합니다.

### 다음 챕터

0. 통합 리팩토링 커밋을 `WORKFLOW.md`에 기록한 모듈·기능 단위 커밋으로 교체한 후
   `job_pipeline/collection.py::retry_after_seconds()`부터 코드 공부를 재개합니다.
   이후 `json_get()`에서 HTTP 429 → Retry-After·점증 대기 → `time.sleep(delay)` →
   재시도 순서를 확인합니다. 작업자의 큐 대기가 아니라 ATS API 재시도 대기를 다룹니다.
   `main.py`와 `manage.py`는 현재 유지합니다. Django 명령으로 수집을 통일하는 방향은
   논의만 했으며 아직 구현하지 않았습니다. Git은 사용자가 실행하며 확인 전에는
   분리 커밋 완료로 기록하지 않습니다.
1. 리팩토링 연결 검사·Django 검사를 먼저 실행하고 실제 ATS API 수집 결과를 확인합니다. 비자 조건이 명시된 결과를 살펴보고 추천 전에 날짜·접수 상태
   확인을 개선합니다.
2. 구현된 Ollama 게시판 발견 검색어와 결과를 확인하고, 선택적 직접 DDGS 공고 검색에도
   프로필 기반 검색어 생성을 연결합니다.
3. Django 화면과 작업자를 검증한 뒤 정기 실행·배포 설정을 연결합니다.
4. 근거 분류를 신뢰할 수 있게 되면 이력서 매칭을 추가합니다.
