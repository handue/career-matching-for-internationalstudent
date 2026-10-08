# Job Analysis Workflow / 채용 공고 분석 흐름

## English

The steps below describe the legacy single-posting Greenhouse workflow, kept
as reference code. The planned discovery flow uses DDGS search; the probe is
not yet connected to analysis and saving. Scheduled collection and application
recommendations are not implemented yet.

1. `scripts/fetch_greenhouse_job.py` requests a posting from the Greenhouse
   API. It saves title, company, location, and cleaned description as a `.txt`
   file. A neighboring `.json` file holds the original URL, board, job ID, and
   fetch time.
2. `scripts/analyze_job.py` reads the `.txt` file and sends its contents to a
   local Ollama model. It returns six independent `yes`, `no`, or `unknown`
   statuses with source evidence.
3. `scripts/save_job_analysis.py` runs the analyzer and saves its result with
   the source metadata. `scripts/job_record.py` defines and validates the saved
   JSON structure.
4. `scripts/list_job_analyses.py` reads the saved results and filters them by
   category and status. `unknown` remains available; it means the posting did
   not establish a clear answer.

`scripts/check_samples.py` is a separate regression check. It compares the
analyzer with the expected answers for fictional postings; it is not model
training or a measure of accuracy on real jobs.

Fetched text and analysis results live under ignored `data/results/`. A saved
result does not confirm an applicant's eligibility or guarantee that the
posting is still open.

## 한국어

아래는 참고용으로 남긴 이전 Greenhouse 단일 공고 처리 흐름입니다. 새 공고 검색은
DDGS로 시험 중이며 검색 결과를 분석·저장 단계에 아직 연결하지 않았습니다.
정기 수집과 지원처 추천도 아직 구현하지 않았습니다.

1. `scripts/fetch_greenhouse_job.py`가 Greenhouse API에서 공고를 가져옵니다.
   제목·회사·지역·정리한 본문을 `.txt`로 저장하고, 옆의 `.json`에 원문 URL,
   게시판 이름, 공고 ID, 수집 시각을 저장합니다.
2. `scripts/analyze_job.py`가 `.txt`를 읽어 로컬 Ollama 모델에 전달합니다.
   여섯 항목을 각각 `yes`, `no`, `unknown`으로 판단하고 원문 근거를 반환합니다.
3. `scripts/save_job_analysis.py`가 분석기를 실행하고 결과와 출처 정보를
   함께 저장합니다. `scripts/job_record.py`는 저장 JSON의 구조를 정의하고
   실제 값을 검증합니다.
4. `scripts/list_job_analyses.py`가 저장 결과를 읽고 항목·상태별로
   조회합니다. `unknown`도 볼 수 있으며, 공고에서 확실한 답을 확인하지
   못했다는 뜻입니다.

`scripts/check_samples.py`는 별도의 회귀 검사 도구입니다. 가상 공고의
기대값과 분석 결과를 비교하며, 모델 학습이나 실제 공고 정확도 측정은
아닙니다.

수집 텍스트와 분석 결과는 Git에서 제외한 `data/results/` 아래에 있습니다.
저장 결과는 지원자의 자격이나 공고의 현재 상태를 보장하지 않습니다.
