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

### 2026-10-01 — Answer key and STEM OPT

- Added fictional postings covering all five categories and
  `samples/expected_statuses.json` as an evaluation key, not training data.
- Found that the model sometimes paraphrased evidence; the code now copies
  the selected sentence from the original posting.
- Added STEM OPT status and evidence separately from ordinary OPT.
- Checked the expected states and source sentences on six fictional postings.
- Created the initial Git commit and this dated log. GitHub publishing is
  performed by the user.
- Added parallel English/Korean documentation, docstrings, and CLI messages.
- Remaining gaps: no real job collection, website, or CPT/H-1B/green-card
  classifier. Complex HTML and bullet formatting still need evaluation.

### Next chapters

1. Classify CPT independently of OPT and STEM OPT.
2. Add separate H-1B and employment-based permanent-residence categories.
3. Collect real postings and measure accuracy against human-reviewed labels.

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

### 2026-10-01 — 정답표와 STEM OPT

- 다섯 항목을 다루는 가상 공고와 검증용
  `samples/expected_statuses.json` 정답표를 만들었습니다.
- 모델이 근거를 바꾸어 쓰는 사례를 발견해 코드가 공고 원문 문장을
  가져오도록 수정했습니다.
- 일반 OPT와 별도로 STEM OPT 상태와 근거를 추가했습니다.
- 가상 공고 6개에서 기대 상태와 원문 근거를 확인했습니다.
- 첫 Git 커밋과 날짜별 진행 기록을 만들었습니다. GitHub 업로드는
  사용자가 직접 진행합니다.
- README·진행 기록·코드 설명·CLI 메시지를 한글/영어로 병기했습니다.
- 남은 범위: 실제 공고 수집, 웹 화면, CPT·H-1B·영주권 분류는 미구현.
  복잡한 HTML과 불릿 형식도 추가 평가가 필요합니다.

### 다음 챕터

1. CPT를 OPT·STEM OPT와 독립적으로 분류합니다.
2. H-1B와 취업 기반 영주권을 각각 추가합니다.
3. 실제 공고를 수집해 사람이 확인한 정답과 정확도를 비교합니다.
