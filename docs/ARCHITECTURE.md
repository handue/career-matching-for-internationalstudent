# Architecture / 프로그램 구조

## Responsibilities / 역할

| Area / 위치 | Responsibility / 역할 | Used by / 사용처 |
|---|---|---|
| `web_config/` | Django configuration and routing / Django 설정·라우팅 | `manage.py`, ASGI/WSGI |
| `jobs/` | HTTP, authentication, DB models, collection queue / 요청·로그인·DB·큐 | Browser and Django worker / 브라우저·작업자 |
| `job_pipeline/` | Framework-independent collection and analysis / 웹 프레임워크와 독립적인 수집·분석 | CLI and worker child process / CLI·작업자 자식 프로세스 |
| `config/` | Inputs, profile, fallback queries / 입력·프로필·대체 검색어 | Discovery and collection / 발견·수집 |
| `samples/`, `tests/` | Regression inputs and checks / 회귀 검사 입력·검사 | Developer commands / 개발자 명령 |
| `data/` | Local generated outputs / 로컬 생성 결과 | Pipeline and DB importer / 처리 흐름·DB 가져오기 |

`web_config` does not contain business logic. Django's `jobs` app bridges the
reusable pipeline into web behavior. Python functions do not need to become
Django classes just to run behind a website. / `web_config`는 설정 패키지입니다.
실제 연동은 `jobs`에서 담당하며 수집·AI 함수 자체를 Django 클래스로 바꿀 필요는 없습니다.

## Read in this order / 코드 읽는 순서

1. `main.py` → `job_pipeline/cli.py`: command entry and arguments / 실행 입구·옵션.
2. `job_pipeline/pipeline.py`: `PipelineOptions`, `run_pipeline` coordinate all stages / 전체 단계 조율.
3. `discovery/queries.py` → `discovery/boards.py`: profile → Ollama query → DDGS URL → ATS API verification → registry / 검색어 생성·게시판 확인·등록.
4. `collection.py`: four API adapters, US filtering, 429 retry, report saving / API 수집·미국 필터·재시도·저장.
5. `analysis/reports.py` → `analysis/extraction.py`: freshness checks → `analyze_file` → `analyze_posting` → Ollama → validated JSON / 시각 검사·본문 분석·검증·저장.
6. `records.py`, `storage.py`: record contracts and CLI listing / 공통 타입·검증·조회.
7. `jobs/models.py` → `views.py` → `management/commands/run_collection_worker.py` → `services.py`: web queue → worker → SQLite import / 웹 큐·작업자·DB 저장.

`search.py` is the optional direct DDGS search/page-reading route; ATS
collection does not scrape every posting through it. / 직접 DDGS 검색·페이지 추출은
보조 경로이며 기본 ATS 수집은 이 경로로 모든 공고를 크롤링하지 않습니다.

## Web flow / 웹 동작

```text
Browser / 브라우저
  → jobs.views: POST collection options / 수집 옵션 전달
  → CollectionJob: queued; HTTP 202 returned / DB 등록 후 즉시 응답
  → run_collection_worker: separate process / 웹 서버와 별도 작업자
  → python -m job_pipeline.cli: child process, log, 30-minute timeout / 자식 프로세스·로그·시간 제한
  → run_pipeline
      → optional discovery: Ollama queries → DDGS → ATS verification / 선택적 게시판 발견
      → ATS API collection → US filter → text and report / 미국 공고 수집·보고서
      → analyze_report → analyze_posting → Ollama / 후보 분석
      → validated analysis JSON / 검증된 분석 저장
  → jobs.services.import_analyses → JobAnalysis in SQLite / DB 가져오기
  → CollectionJob: completed or failed / 작업 상태 기록
  → Browser polls status and displays stored results / 상태 조회·공고 표시
```

CLI calls the same `run_pipeline` through `main.py`. Per-posting analysis now
calls a Python function directly; it no longer launches the extraction CLI and
parses console output. Only the whole workflow is process-isolated by the Django
worker for timeout/log handling. / CLI도 같은 흐름을 호출합니다. 공고별 분석은 함수 직접
호출로 바뀌었으며 Django 작업자는 전체 흐름만 프로세스로 격리합니다.

HTTP 429 waits happen in the child process, so they do not block the web request.
This is a local single-worker design; multiple workers need isolated output
paths and a stronger queue. / 재시도 대기는 자식 프로세스에서 하며 웹 요청을 막지 않습니다.
여러 작업자로 확대하려면 실행별 출력 경로와 큐 구조 보강이 필요합니다.

## File migration / 파일 이동

| Before / 이전 | Now / 현재 |
|---|---|
| `scripts/collect_ats_jobs.py` | `job_pipeline/collection.py` |
| `scripts/discover_ats_boards.py` | `job_pipeline/discovery/boards.py` |
| `scripts/plan_ats_queries.py` | `job_pipeline/discovery/queries.py` |
| `scripts/probe_job_search.py` | `job_pipeline/search.py` |
| `scripts/analyze_job.py` | `job_pipeline/analysis/extraction.py` |
| `scripts/analyze_search_results.py` | `job_pipeline/analysis/reports.py` |
| `scripts/job_record.py` | `job_pipeline/records.py` |
| `scripts/list_job_analyses.py` | `job_pipeline/storage.py` |
| Main workflow body / main 처리 본문 | `job_pipeline/pipeline.py`; options in `cli.py` / 옵션은 `cli.py` |

Removed the unused `scripts/legacy_greenhouse/` and `scripts/background_jobs.py`.
Django's queued worker replaces `--background`. Kept samples, tests, migrations,
input configurations, generated text/JSON, and teaching comments. Output paths
and saved record format remain compatible; no DB model change was made.
/ 미사용 이전 코드·독립 백그라운드 실행기를 제거했습니다. 샘플·검사·마이그레이션·설정·
생성 데이터·학습 주석은 유지했습니다. 결과 경로·저장 형식은 호환되며 DB 모델은 변경하지 않았습니다.

The refactor fixes an error path too: zero collected jobs with failed ATS boards
now returns failure rather than success. / 수집 결과가 0건인데 ATS 실패가 있으면 성공으로
처리하던 경로도 실패 코드로 수정했습니다.

## Second audit, 2026-10-11 / 재점검

- Collapsed single-file collection/search packages into `collection.py` and
  `search.py`, removing two unnecessary package initializers. / 파일 하나뿐인 수집·검색
  패키지를 단일 모듈로 줄이고 불필요한 초기화 파일 두 개를 제거했습니다.
- Centralized default configuration paths in `paths.py` and option rules in
  `pipeline.validate_options`. / 기본 설정 경로·옵션 검사 구현을 각각 한곳에 모았습니다.
- Discovery and collection now use `collection.read_boards`; both validate the
  provider and board token and normalize provider names. / 발견·수집이 같은 게시판 설정
  검사 함수를 사용하며 플랫폼 이름을 소문자로 정리합니다.
- Kept separate query planning vs posting extraction, discovery vs collection,
  and CLI JSON listing vs Django DB listing because their inputs and responsibilities
  differ. / 검색어 생성·본문 분석, 발견·수집, JSON CLI 조회·DB 웹 조회는 역할이 달라 유지했습니다.
- Kept Django's migrations, package initializers, and ASGI/WSGI entry points;
  these are framework/deployment artifacts, not duplicate business logic.
  / Django 마이그레이션·패키지 초기화·ASGI/WSGI 진입점은 중복 업무 로직이 아닙니다.

The chosen application structure is a small Django project with a reusable
pipeline and a separate worker. It does not require one file per function or
extra layers solely to resemble a large service. / 작은 Django 프로젝트에 공통 처리
모듈·별도 작업자를 두는 구조를 채택하며 함수마다 파일을 만들거나 불필요한 계층을 추가하지 않습니다.

Production deployment is still pending. Current findings: fixed shared `latest.json`
paths, worker imports of all historical analysis files, local-only process lock,
SQLite, and development-default settings. Before concurrent collection, isolate
reports/output by job and import only that run's results; replace local locking
with atomic queue claims if adding workers. A single-process local queue does not
require Celery/Redis by default. / 운영 배포는 아직 미완료입니다. 공통 보고서 경로·전체 과거
결과 재가져오기·로컬 잠금·SQLite·개발 기본 설정이 남아 있습니다. 동시 수집 전에는
작업별 출력·가져오기 범위를 분리하고 여러 작업자에 맞는 큐 선점 처리가 필요합니다.
개인용 단일 작업자 구조에 Celery·Redis를 무조건 추가할 필요는 없습니다.

Deployment requires a production WSGI/ASGI server, environment-specific secrets,
DEBUG disabled, HTTPS/static-file handling, monitoring/backups, and checks against
production settings. See [Django's deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
/ 운영 서버·환경별 설정·HTTPS·정적 파일·로그·백업·운영 설정 검사는 공식 배포 안내를 따릅니다.
No project execution or tests were performed by the assistant. / 도우미는 프로그램·테스트를 실행하지 않았습니다.
