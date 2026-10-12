# Career Matching for International Students

A personal project that collects US job postings, uses local Ollama to extract
job requirements and immigration-support statements, and displays saved results
in Django. / 미국 공고를 수집하고 로컬 Ollama로 요구 조건·이민 지원 문구를 분석한
뒤 Django에서 조회하는 개인 프로젝트입니다.

The six independent categories are CPT, OPT, STEM OPT, visa sponsorship, H-1B,
and green-card sponsorship. Each uses `yes`, `no`, or `unknown` with source
evidence. Missing information remains `unknown`; a category is not a guarantee
of personal eligibility. / 여섯 항목을 독립적으로 분류하며 정보가 없으면 `unknown`입니다.
분류 결과만으로 개인의 지원 자격이 확정되지는 않습니다.

## Structure / 구조

```text
career-match/
├── main.py                    # CLI entry / CLI 진입점
├── manage.py                  # Django management / Django 관리 명령
├── web_config/                # Settings, URLs, ASGI/WSGI / 설정·라우팅
├── jobs/                      # Views, DB, queue, worker / 화면·DB·큐·작업자
├── job_pipeline/              # Reusable Python logic / 재사용 Python 로직
│   ├── cli.py                 # Arguments / 실행 옵션
│   ├── pipeline.py            # Workflow / 전체 흐름
│   ├── paths.py               # Project paths / 공통 경로
│   ├── records.py             # Types and validation / 타입·검증
│   ├── storage.py             # Saved JSON listing / 저장 JSON 조회
│   ├── discovery/             # Ollama queries, DDGS board discovery / 검색어·게시판 발견
│   ├── collection.py          # Public ATS APIs / 공개 ATS API 수집
│   ├── search.py              # Optional DDGS page search / 선택적 페이지 검색
│   └── analysis/              # Ollama extraction and saving / AI 분석·저장
├── config/                    # Profile, boards, fallback queries / 입력 설정
├── samples/                   # Fictional regression inputs / 가상 검사 입력
├── tests/                     # Pipeline and AI sample checks / 처리 흐름·AI 검사
├── docs/                      # Instructions and dated log / 안내·날짜별 기록
└── data/                      # Local results/private files / 로컬 결과·개인 파일
```

Read [Architecture](docs/ARCHITECTURE.md) for file mappings and call order,
[Workflow](docs/WORKFLOW.md) for CLI commands, [Django](docs/DJANGO.md) for web
setup, and [Progress](docs/PROGRESS.md) for dated history. / 파일 이동·호출 순서는
구조 문서, CLI 명령은 흐름 문서, 웹 실행은 Django 문서, 날짜별 기록은 진행 기록을 봅니다.

## Entry points and study checkpoint / 실행 입구·학습 재개 위치

`main.py` delegates to `job_pipeline.cli` for terminal collection and analysis.
`manage.py` runs Django commands: the web server, migrations, tests, and the
collection worker. The worker launches `python -m job_pipeline.cli`; it does not
depend on `main.py`. Both entry points are currently retained; collection has
not been consolidated into a `manage.py collect_jobs` command.
/ `main.py`는 터미널 수집·분석 입구이며 `manage.py`는 Django 관리 명령 입구입니다.
작업자는 패키지 CLI를 실행하므로 `main.py`에 의존하지 않습니다. 현재 두 입구를 유지하며
수집을 `manage.py collect_jobs` 명령으로 통일하는 변경은 아직 하지 않았습니다.

After committing the refactor, resume studying
[`job_pipeline/collection.py`](job_pipeline/collection.py) at
`retry_after_seconds()`, then follow `json_get()` and its HTTP 429 retry loop.
Focus on `Retry-After`, the fallback waits of 1 and 2 seconds, and
`time.sleep(delay)` before the next request. This is API retry waiting, not the
worker's idle queue polling sleep. The current implementation makes at most
three attempts including the initial request and skips a board if the requested
wait exceeds 30 seconds.
/ 리팩토링 커밋 후 `collection.py`의 `retry_after_seconds()`부터 다시 공부하고
`json_get()`의 HTTP 429 재시도 흐름으로 이어갑니다. 서버의 `Retry-After`, 기본 1·2초
대기, 다음 요청 전 `time.sleep(delay)`를 살펴봅니다. 작업 큐의 대기 sleep이 아니라
API 재시도 대기입니다. 최초 요청을 포함해 최대 3회 시도하며 서버가 요구한 대기가
30초를 넘으면 해당 게시판을 건너뜁니다.

## Setup and checks / 설치·검사

Run commands from the project root. Check installed packages before installing
missing dependencies. The user runs commands; the assistant edits code. / 프로젝트
루트에서 실행하고 설치 여부를 먼저 확인합니다. 실행은 사용자가 진행합니다.

```bash
.venv/bin/python -m pip show Django ddgs beautifulsoup4
# If missing / 필요한 패키지가 없으면:
.venv/bin/python -m pip install -r requirements-web.txt

# Offline wiring checks / 네트워크 없는 연결 검사:
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test jobs
```

Pylance reads `pyrightconfig.json`. If Pyright CLI is already installed, run
`pyright` for the same project scope. Type hints do not replace runtime JSON
validation. / Pylance가 타입 설정을 읽습니다. Pyright CLI를 설치한 경우 `pyright`로도
검사할 수 있으며 외부 JSON은 실행 중에도 검증합니다.

## Web / 웹 실행

First-time database setup and login creation / 최초 DB·계정 준비:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py import_analyses
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Open <http://127.0.0.1:8000/>. In a second terminal, start the worker; keep Ollama
running in its app or with `ollama serve` in another terminal. / 웹에 접속하고 다른
터미널에서 작업자를 실행합니다. Ollama 앱 또는 별도 터미널의 `ollama serve`도 필요합니다.

```bash
.venv/bin/python manage.py run_collection_worker
```

The web request queues work and returns immediately; the worker runs collection
and analysis and imports JSON results into SQLite. / 웹 요청은 큐 등록 후 즉시 반환하고
별도 작업자가 수집·분석·SQLite 저장을 담당합니다.

## CLI / CLI 실행

```bash
# Default ATS collection and analysis / ATS 수집·분석:
.venv/bin/python main.py --search-limit 5 --analyze-limit 1

# Discover boards using profile-based Ollama queries first / 프로필 기반 게시판 발견 포함:
.venv/bin/python main.py --discover --search-limit 10 --analyze-limit 3

# Inspect saved records / 저장 결과 조회:
.venv/bin/python -m job_pipeline.storage --category opt --status unknown

# AI regression check: requires Ollama / AI 회귀 검사: Ollama 필요:
.venv/bin/python tests/check_samples.py
```

Do not run CLI collection concurrently with the Django worker: report files are
shared. / 수집 CLI와 Django 작업자는 보고서 파일을 공유하므로 동시에 실행하지 않습니다.
The old `scripts/...` commands and `--background` option were removed; current
module commands are in [Workflow](docs/WORKFLOW.md). / 이전 명령을 대체하는 새 명령은
흐름 문서에 정리했습니다.

## Current limits / 현재 범위

- Public APIs: Greenhouse, Lever, Ashby, SmartRecruiters. DDGS finds new boards
  and can optionally search individual pages. / 공개 ATS API가 기본이며 DDGS는 발견·보조 검색입니다.
- US filtering uses explicit country/state evidence; city-only ambiguous
  locations can be missed. / 국가·주 근거로 미국을 필터하며 도시명만 있는 공고는 누락될 수 있습니다.
- Ollama generates discovery queries from `config/search_profile.json`, with
  fixed queries only as fallback. Direct DDGS mode still takes a manual query.
  / 게시판 발견 검색어는 AI가 생성하며 직접 DDGS 모드는 수동 쿼리를 받습니다.
- Runtime result limits are configurable project settings, not ATS quotas.
  DDGS's current 1–10 bound is an experimental guard; real usage should consider
  page count, elapsed time, and retry behavior. / 개수 제한은 API 할당량이 아니며 실제
  사용에서는 페이지 수·실행 시간·재시도를 함께 고려해야 합니다.
- Search snippets and HTTP 200 do not prove applications are open. Known past
  deadlines/closed pages are skipped; missing dates stay unknown.
  / 검색 요약·접속 성공만으로 모집 중이라고 판단하지 않습니다.
- Local single-worker SQLite queue; scheduling, resume uploads, embedding
  matching, ranking, and production deployment remain future work.
  / 현재 로컬 단일 작업자이며 정기 실행·레쥬메 업로드·임베딩 매칭·순위·배포는 미구현입니다.

Generated results, private files, `.env`, SQLite, and caches are excluded from
Git. Commit code/configuration/documentation, never resumes or secrets. / 생성 결과·개인
파일·비밀 값은 Git에서 제외합니다. 이번 리팩토링은 사용자 실행 검증 전입니다.
