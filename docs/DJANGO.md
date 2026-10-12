# Django Web and Worker / Django 웹과 작업자

## English

Django 5.2 LTS provides the first local web interface. Check the existing
environment before installing dependencies:

```bash
.venv/bin/python -m pip show Django
```

`requirements-web.txt` includes Django and the existing search dependencies.
Install it if the required versions are missing, then set up the database,
check the project, import saved analyses, and create your login:

```bash
.venv/bin/python -m pip install -r requirements-web.txt
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py migrate
.venv/bin/python manage.py test jobs
.venv/bin/python manage.py import_analyses
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Open <http://127.0.0.1:8000/> and sign in. Existing saved analyses are copied
into SQLite, deduplicated by original posting URL. The dashboard filters all
six categories by `yes`, `no`, or `unknown` and displays the original evidence
and source link. It shows the first 100 matching results.

Start the worker in another terminal, from the project root:

```bash
.venv/bin/python manage.py run_collection_worker
```

Ollama must be running for discovery query generation and posting analysis.
Click **Start collection** on the dashboard. The POST endpoint creates a
`queued` database row and returns HTTP 202 with a job ID; it does not call
ATS APIs, run Ollama, or sleep. The browser polls the status endpoint.
The worker processes one task at a time, runs `python -m job_pipeline.cli` in a child process with
`subprocess.run`, imports saved analyses, and writes `completed` or `failed`.
Only the worker waits during HTTP 429 retries. Without a worker, requests
remain `queued` and the dashboard is still usable.

The database queue persists across normal restarts. An exclusive local file
lock prevents two Django workers from overwriting shared CLI report files.
On startup, the worker marks interrupted `running` jobs failed; it does not
silently rerun them. Each run has a 30-minute timeout and its own log under
ignored `data/results/django_worker/`. Do not run CLI collection concurrently with this worker: they share file paths.
The standalone `--background` option has been removed in favor of this queue.
This is a local single-worker implementation, not a deployed multi-worker queue.

Routes:

| Method | URL | Purpose |
|---|---|---|
| GET | `/` | Signed-in analysis dashboard |
| POST | `/api/collection-jobs/` | Enqueue form-encoded collection options; CSRF required |
| GET | `/api/collection-jobs/<job_id>/` | Read the signed-in user's task status |
| GET | `/admin/` | Django administration |

Read the code in this order: `web_config/settings.py`, `jobs/models.py`,
`jobs/urls.py`, `jobs/views.py`, `jobs/services.py`, then
`jobs/management/commands/run_collection_worker.py`.
The `job_pipeline` package owns reusable collection/analysis logic; Django owns HTTP
handling, authentication, stored web results, and task status.

Local settings use SQLite and a development secret. Deployment needs
`DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS`, plus a
production web server and supervised worker. Environment variables are read
from the process; `.env` files are not loaded automatically. Scheduling,
resume uploads, and ranking are not implemented yet. The user runs installation,
migrations, tests, and servers; these changes have not been runtime-validated.

## 한국어

Django 5.2 LTS로 첫 로컬 웹 화면을 추가했습니다. 위의 `pip show Django`로
기존 설치 여부를 먼저 확인하고, 필요한 버전이 없으면 `requirements-web.txt`를
설치합니다. 위 명령을 순서대로 실행해 설정·마이그레이션 검사를 하고 DB를 만든
뒤, 테스트·기존 JSON 분석 가져오기·로그인 계정 생성을 진행합니다.

`runserver` 실행 후 <http://127.0.0.1:8000/>에서 로그인합니다. SQLite에는
원문 URL을 기준으로 중복 없이 기존 분석을 저장합니다. 웹은 여섯 분류의
`yes`, `no`, `unknown` 필터와 근거 문장·원문 링크를 보여줍니다.
조회 결과는 현재 최대 100건을 표시합니다.

다른 터미널에서 `manage.py run_collection_worker`를 실행합니다. Ollama도
실행되어 있어야 검색어 생성과 공고 분석이 가능합니다. 화면의 **Start collection**을
누르면 웹 API는 DB에 `queued` 작업을 등록하고 HTTP 202와 작업 ID를 즉시
반환합니다. 웹 요청 안에서는 ATS·Ollama 호출이나 `sleep()`을 실행하지 않습니다.
브라우저는 상태 API를 주기적으로 조회합니다.

작업자는 한 번에 작업 하나를 꺼내 `python -m job_pipeline.cli`를 실행하고 분석을 DB에
가져온 뒤 `completed` 또는 `failed`를 기록합니다. 429 재시도 대기는
이 작업자에서만 일어납니다. 작업자를 실행하지 않으면 작업은 `queued`로
남지만 저장된 공고를 조회하는 웹은 계속 동작합니다.

작업 큐는 DB에 남으며 로컬 파일 잠금으로 Django 작업자 두 개가 동시에
실행되지 않게 합니다. 작업자 재시작 시 중단된 `running` 작업은 실패 처리하고
자동 재실행하지 않습니다. 작업마다 최대 30분을 기다리며 로그는 Git 제외 경로인
`data/results/django_worker/`에 남습니다. 수집 CLI는 같은 보고서 경로를 쓰므로
Django 작업자와 동시에 실행하지 않습니다. 기존 `--background` 옵션은 작업 큐로 대체했습니다.
현재는 로컬 단일 작업자 구조이며 배포용 여러 작업자 시스템은 아닙니다.

코드는 `web_config/settings.py` → `jobs/models.py` → `jobs/urls.py` →
`jobs/views.py` → `jobs/services.py` →
`jobs/management/commands/run_collection_worker.py` 순서로 읽습니다.
`job_pipeline`의 재사용 Python 모듈은 수집·분석을 담당하고, Django는 웹 요청·로그인·DB 조회와
작업 상태를 담당합니다.

배포 시에는 `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
운영용 웹 서버와 관리되는 작업자 실행이 필요합니다. 환경 변수는 프로세스에서 읽으며
`.env` 파일을 자동으로 읽지는 않습니다. 정기 실행·레쥬메 업로드·추천 순위는 아직
없습니다. 설치·마이그레이션·테스트·서버 실행은 사용자가 진행하며, 이번 변경은
아직 실행 검증 전입니다.

## Folder layout / 폴더 구조

```text
career-match/
├── manage.py              # Django CLI / Django 관리 명령
├── web_config/            # Django settings and routing / Django 설정·라우팅
├── jobs/                  # Web app, DB models, worker / 웹 앱·DB 모델·작업자
│   ├── migrations/        # DB schema history / DB 구조 변경 기록
│   ├── templates/         # Web templates / 웹 화면
│   └── management/commands/ # Worker and import CLI / 작업자·분석 가져오기 명령
├── job_pipeline/          # Reusable collection and analysis / 재사용 수집·분석 모듈
│   ├── discovery/         # Ollama queries and DDGS / AI 검색어·게시판 발견
│   ├── collection.py      # Public ATS APIs / 공개 ATS API
│   ├── search.py          # Optional page search / 보조 페이지 검색
│   └── analysis/          # Ollama extraction and saving / AI 분석·저장
├── config/                # Search profile and ATS inputs / 검색 프로필·ATS 입력
├── samples/               # Fictional regression examples / 가상 회귀 검사 예제
├── tests/                 # CLI sample checker / CLI 샘플 검사기
├── docs/                  # Setup, workflow, development log / 실행·흐름·개발 기록
└── data/                  # Local generated/private data (ignored) / 로컬 생성·개인 데이터 (Git 제외)
```

`jobs/tests.py` checks Django's HTTP and DB behavior; `tests/check_samples.py`
checks the AI extraction CLI. The project folder and Django settings package
have different names to clarify their roles.

`jobs/tests.py`는 Django HTTP·DB 동작을 검사하고 `tests/check_samples.py`는
AI 분석 CLI를 검사합니다. 프로젝트 전체와 Django 설정 패키지의 역할을 구분하기
위해 서로 다른 이름을 사용합니다.

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed call order and migrated file names.
/ 자세한 호출 순서와 이동한 파일 이름은 구조 문서를 확인합니다.
