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

At this checkpoint, the reviewable project consists of the analyzer, sample
checker, 16 fictional postings, their answer key, README, and the real-posting
review. The 96/96 result is a fictional-sample check, not a measured accuracy
rate on live job postings.

### Next chapters

1. Collect real postings and measure accuracy against human-reviewed labels.
2. Build a simple interface for viewing classifications and their evidence.
3. Add resume-based matching once source classification is reliable.

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

이 시점에 검토 가능한 범위는 분석기, 샘플 검사기, 가상 공고 16개와
정답표, README, 실제 공고 검토 기록입니다. 96/96 통과는 가상 샘플
검사 결과이며 실제 공고에 대한 정확도 수치는 아닙니다.

### 다음 챕터

1. 실제 공고를 수집해 사람이 확인한 정답과 정확도를 비교합니다.
2. 분류 결과와 근거를 보여주는 간단한 화면을 만듭니다.
3. 근거 분류를 신뢰할 수 있게 되면 이력서 매칭을 추가합니다.
