# Career Match

[날짜별 진행 기록](docs/PROGRESS.md)

미국 유학생을 위해 채용 공고의 CPT, OPT, STEM OPT 수용 여부와
H-1B, 취업 기반 영주권 지원 여부를 근거 문장과 함께 찾는 프로젝트입니다.

## 첫 목표

가상 공고를 로컬 Qwen3-8B로 분석해 일반 OPT와 STEM OPT 수용 여부를
각각 `yes / no / unknown`으로 분류합니다. 이 단계는 공고 수집 기능이 아닌
모델 연결과 분류 기준 확인입니다.

1. 기존 Anaconda Python 3.13.9 사용, 프로젝트 `.venv` 생성 완료
2. Ollama 0.34.4 설치 완료 (`brew install ollama`)
3. 별도 터미널에서 `ollama serve` 실행
4. `ollama pull qwen3:8b`로 모델 다운로드 (약 5.2GB)
5. 아래 명령으로 분석

```bash
cd /Users/anjung/coding/career-match
/opt/homebrew/anaconda3/bin/python -m venv .venv
source .venv/bin/activate
python scripts/analyze_job.py
```

외부 Python 패키지는 아직 필요하지 않습니다. 입력만 확인하려면
`python scripts/analyze_job.py --dry-run`을 실행하세요.

다른 샘플을 분석하려면 `--file samples/job_sponsorship_yes.txt`처럼
파일 경로를 지정합니다. 제공된 공고는 모두 가상 데이터입니다.

`samples/expected_statuses.json`은 5개 제도별 기대값입니다.
`visa_all_yes.txt`, `visa_all_no.txt`, `visa_all_unknown.txt`,
`visa_mixed.txt`는 긍정·부정·무언급·혼합 표현을 담습니다.
`job.txt`는 일반적인 비자 스폰서십 문구만으로 특정 제도를
추론하지 않는지 확인합니다. 이 파일들은 모델 학습용 데이터가 아닙니다.

Ollama 서버는 현재 터미널 세션으로 실행합니다. 재부팅 후에는 다시
`ollama serve`를 실행해야 합니다. 로그인 시 자동 실행은 설정하지 않았습니다.
Homebrew는 Ollama의 의존성으로 Python 3.14도 설치했지만,
프로젝트 `.venv`는 기존 Python 3.13.9를 사용합니다.

## 결과 확인

2026-09-30 가상 공고 3개를 로컬 Qwen3-8B로 실행해 OPT 분류를 확인했습니다.

| 샘플 | 기대 OPT 상태 | 실제 상태 |
| --- | --- | --- |
| `job_opt_yes_h1b_no.txt` | yes | yes |
| `job_opt_no.txt` | no | no |
| `job.txt` (비자 스폰서십 불가만 명시) | unknown | unknown |

처음에는 모델이 일반적인 비자 스폰서십 불가를 OPT 불가로 오해했습니다.
OPT 상태가 `yes` 또는 `no`이려면 원문 근거에 OPT가 직접 언급되어야
한다는 검사를 추가했습니다. 이 가상 예제 3개가 맞았다고
실제 공고의 정확도가 보장되는 것은 아닙니다.

처음 새 5제도 샘플을 OPT 전용 분석기에 넣었을 때 두 오류가 나왔습니다.
모델이 STEM OPT 문장을 일반 OPT의 근거로 사용했고, 근거 문장을 원문과
다르게 반환했습니다. 공고에서 일반 OPT 문장만 미리 찾아 모델에 제공하고,
근거는 해당 원문 문장에서 코드가 채우도록 바꿨습니다.

수정 후 새 샘플과 일반 비자 스폰서십 샘플의 결과:

| 샘플 | OPT 기대값 | 현재 결과 |
| --- | --- | --- |
| `visa_all_yes.txt` | yes | yes |
| `visa_all_no.txt` | no | no |
| `visa_all_unknown.txt` | unknown | unknown |
| `visa_mixed.txt` | yes | yes |
| `job.txt` | unknown | unknown |

현재 문장 분리는 문장부호 뒤 공백을 기준으로 하는 간단한 방식입니다.
실제 공고의 불릿·HTML·줄바꿈과 복잡한 표현은 아직 검증하지 않았습니다.
CPT·H-1B·영주권은 아직 코드에 구현하지 않았습니다.

2026-10-01에 STEM OPT를 별도 필드로 추가했습니다. 아래 6개 가상 공고에서
일반 OPT와 STEM OPT의 기대값이 모두 맞았고, 근거도 원문 문장이었습니다.

| 샘플 | OPT | STEM OPT |
| --- | --- | --- |
| `visa_all_yes.txt` | yes | yes |
| `visa_all_no.txt` | no | no |
| `visa_all_unknown.txt` | unknown | unknown |
| `visa_mixed.txt` | yes | no |
| `job_opt_yes_h1b_no.txt` | yes | unknown |
| `job_stem_opt_yes_only.txt` | unknown | yes |

코드는 출력 형식과 OPT·STEM OPT 근거 문장의 존재를 확인하지만 모든 내용의 정확성을 보장하지 않습니다.
최초 실행에서는 모델 로딩 시간이 추가될 수 있습니다.

## 챕터별 진행

1. **OPT·STEM OPT 분류:** 각각의 yes/no/unknown과 원문 근거 확인 (완료)
2. **나머지 제도:** CPT, H-1B, 취업 기반 영주권을 각각 분류
3. **공고 수집:** 미국 채용 API 연결, SQLite에 원문·확인 날짜 저장
4. **검색 화면:** 제도별 필터, 근거 문장, 공고 원문 링크 표시
5. **개인화:** 이력서와 직무 선호를 반영한 추천 추가

각 챕터가 끝날 때 실행 결과를 함께 확인한 다음 다음 챕터로 진행합니다.

회원가입, 모델 학습, 자동 지원은 초기 범위에 포함하지 않습니다.
개인 데이터와 분석 결과는 Git에 넣지 않습니다.

참고: https://docs.ollama.com/api/chat
