# Workflow and Commands / 처리 흐름·실행 명령

## Default flow / 기본 흐름

Profile → Ollama discovery queries → DDGS board discovery → public ATS API
verification → registered boards → ATS US postings → date/availability checks →
Ollama extraction → validated JSON → Django DB → web filters.
/ 프로필 → AI 검색어 → 게시판 검색 → ATS API 확인 → 게시판 등록 → 미국 공고 수집 →
날짜·접수 상태 검사 → AI 분석 → 검증된 JSON → Django DB → 웹 분류 조회입니다.

Discovery is optional (`--discover`). Existing registered boards can be collected
without running DDGS again. Discovery may revise queries once if too few new
boards are found; fixed JSON queries are fallback inputs. / 게시판 발견은 선택적입니다.
등록된 게시판은 재검색 없이 수집하며 발견 결과가 적으면 검색어를 한 번 수정합니다.

## CLI commands / CLI 명령

From the project root, with dependencies installed and Ollama running:
/ 의존성을 설치하고 Ollama가 실행 중인 상태에서 프로젝트 루트에서 실행합니다.

```bash
# Entire ATS flow / ATS 전체 흐름:
.venv/bin/python main.py --discover --search-limit 10 --analyze-limit 3

# Individual stages for learning/debugging / 학습·디버깅용 개별 단계:
.venv/bin/python -m job_pipeline.discovery.boards --help
.venv/bin/python -m job_pipeline.discovery.boards
.venv/bin/python -m job_pipeline.collection --limit 5
.venv/bin/python -m job_pipeline.analysis.reports --report data/results/ats_collection/latest.json --limit 1
.venv/bin/python -m job_pipeline.storage --category visa_sponsorship --status unknown

# Optional direct DDGS search / 선택적 직접 DDGS 검색:
.venv/bin/python main.py --source ddgs --query 'site:job-boards.greenhouse.io "new grad" "software engineer"' --search-limit 5 --analyze-limit 1

# Search/page extraction only / 검색·본문 추출만:
.venv/bin/python -m job_pipeline.search --query 'site:job-boards.greenhouse.io "new grad" "software engineer"' --limit 5

# Analyze one saved text / 저장 본문 하나 분석:
.venv/bin/python -m job_pipeline.analysis.extraction --file data/results/search_probe/daba7a109d16565a.txt
```

The last example requires that local file; substitute an actual saved path.
Use `--help` for each module's options. / 마지막 예시는 해당 파일이 있어야 하며 실제 저장된
경로로 바꿉니다. 모듈별 옵션은 `--help`로 확인합니다.

## Checks / 검사

```bash
# Compile for syntax; does not call AI / 문법 컴파일 검사: AI 호출 없음:
.venv/bin/python -m compileall -q main.py manage.py job_pipeline web_config jobs tests

# Offline pipeline wiring / 네트워크 없는 처리 흐름 연결 검사:
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'

# Django settings, migration consistency, HTTP/DB behavior / Django 설정·마이그레이션·HTTP·DB:
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test jobs

# Regression samples: actually calls Ollama / 회귀 샘플: 실제 Ollama 호출:
.venv/bin/python tests/check_samples.py
```

Compilation checks syntax, not types or behavior. Pylance checks types using
`pyrightconfig.json`; installed Pyright CLI can also run `pyright`.
/ 컴파일은 문법 검사이며 타입·동작 검사가 아닙니다. 타입은 Pylance 또는 설치된 Pyright로 검사합니다.

## Outputs and limits / 결과·제한

- `data/results/ats_boards_discovered.json`: discovered board registry / 발견 게시판 목록.
- `data/results/ats_collection/`: ATS text and latest report / ATS 본문·보고서.
- `data/results/search_probe/`: DDGS text and latest report / DDGS 본문·보고서.
- `data/results/analyses/`: compatible saved analysis records / 호환되는 분석 저장 결과.
- `data/results/django_worker/`: worker lock and per-job logs / 작업자 잠금·작업 로그.

`search-limit` counts selected postings, not HTTP requests. One board can require
several API requests. Discovery API probes have no project cap unless
`--max-probes` is supplied. ATS 429 responses retry up to three total attempts,
with waits capped at 30 seconds; longer server waits or exhausted attempts fail
that board. / 공고 개수와 요청 횟수는 다릅니다. 발견 확인 횟수는 옵션을 지정할 때만 제한하며
429는 최대 총 3회 시도하고 한 번에 최대 30초 기다립니다.

DDGS's 1–10 result limit is a current experimental guard, not a provider quota.
Real usage needs page-count and elapsed-time budgets, measured against results.
/ DDGS 개수 제한은 시험 단계 설정입니다. 실제 사용은 페이지 수·실행 시간과 결과를 함께 봐야 합니다.

These shared report paths support one collection run at a time. Do not collect
from CLI while the Django worker is active. Web setup and queue operation are in
[DJANGO.md](DJANGO.md). / 현재 보고서 경로를 공유하므로 한 번에 하나만 수집합니다.
웹 실행·큐 사용 방법은 Django 문서에 있습니다.

## Refactor commit plan / 리팩토링 커밋 분리 계획

The combined commit `40ad570` was pushed on 2026-10-11. Replace it with the
following six commits after creating a local backup branch and resetting only
the index/commit pointer; preserve working files. The user runs Git commands.
This plan is not marked completed until the rewritten history is confirmed.
/ 2026-10-11에 올린 통합 커밋 `40ad570`을 백업 브랜치에 보존한 뒤, 작업 파일은
그대로 두고 커밋을 풀어 아래 여섯 개로 나눕니다. Git은 사용자가 실행하며 새 이력이
확인되기 전에는 완료로 기록하지 않습니다.

| Order / 순서 | Commit title / 영어 제목 | Scope / 범위 |
|---|---|---|
| 1 | `refactor: package posting analysis and search modules` | Shared paths/types, search, extraction/report saving, JSON listing, sample checker/fixtures; remove replaced scripts / 경로·타입·검색·분석·조회·샘플 검사 이동 및 대체된 스크립트 제거 |
| 2 | `feat: collect US jobs from public ATS APIs` | Four ATS adapters, US filtering, shared board validation, bounded 429 retries, seed boards / ATS 어댑터·미국 필터·게시판 검증·재시도·초기 설정 |
| 3 | `feat: discover ATS boards with profile-based Ollama queries` | Profile-driven query generation, DDGS discovery, ATS verification, saved registry, fallback queries / 프로필 검색어·발견·API 확인·목록·예비 쿼리 |
| 4 | `refactor: orchestrate collection through a shared pipeline` | Shared options/validation, CLI entry, full workflow and wiring checks / 공통 옵션·검증·CLI·전체 흐름·연결 검사 |
| 5 | `feat: add Django dashboard and collection worker` | Django settings, authentication/dashboard, DB queue/importer, separate worker, HTTP/DB tests, dependencies and ignore/type settings / Django 설정·로그인·화면·DB 큐·작업자·검사·환경 설정 |
| 6 | `docs: document architecture and API retry study checkpoint` | README, workflow, architecture, Django setup and dated progress / README·흐름·구조·Django 안내·진행 기록 |

The initial split includes the sample fixtures required by the moved checker;
worker wiring checks belong with the Django feature. A backup branch allows the
original combined commit to be inspected. Push the replacement with an explicit
lease expecting the original remote commit; a changed remote must reject the push.
/ 이동한 검사기에 필요한 샘플은 첫 커밋에 함께 넣고 작업자 검사는 Django 커밋에 넣습니다.
백업 브랜치로 기존 커밋을 확인할 수 있습니다. 원격이 원래 커밋일 때만 새 이력으로
교체하도록 명시적 lease를 사용하며 원격이 바뀌면 push가 거절됩니다.
