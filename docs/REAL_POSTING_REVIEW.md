# Real Posting Review / 실제 공고 검토

Reviewed 2026-10-01 / 검토일 2026-10-01

## English

This is an exploratory check of short excerpts from employer job pages, not an
accuracy estimate. Each status records what the excerpt supports. Job pages can
change or close, so the original page must be checked before applying.

| Employer page | What was checked | Observed result |
| --- | --- | --- |
| [Nearform](https://job-boards.greenhouse.io/nearform/jobs/7619114003) | General visa refusal | Visa sponsorship `no`; other categories `unknown` |
| [RoboForce](https://job-boards.greenhouse.io/roboforce/jobs/5290821008) | Conditional immigration support | Visa sponsorship `yes`, green card `yes`; H-1B `unknown` |
| [Cloudflare](https://job-boards.greenhouse.io/cloudflare/jobs/8199958) | Applicant question about CPT/OPT | CPT and OPT `unknown` |
| [FORTUNE](https://boards.greenhouse.io/embed/job_app?token=5424161004) | Applicant question mentioning STEM OPT, H-1B and green card | All three `unknown` |
| [ID.me](https://job-boards.greenhouse.io/idmeuniversityrecruiting/jobs/7980382003) | E-Verify statement | STEM OPT `unknown` |
| [Adyen](https://job-boards.greenhouse.io/adyen/jobs/8128101) | Visa transfers supported; new H-1B CAP filings refused | H-1B and general visa sponsorship `unknown` because support depends on the case |

The [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html) returned
the complete Nearform posting without authentication. A full-posting run also
returned general visa sponsorship `no` with a matching source sentence. Its
`content` field contained escaped HTML, which required HTML unescaping before
tag removal. A first pass that skipped this step left tags in the evidence.
The current analyzer still accepts plain text only; API retrieval and HTML
conversion are implementation work for the next chapter.

The six excerpts omit most of each posting. They check specific wording only,
not title, skill or experience extraction quality. The temporary copies used
for this review are under ignored `data/results/` and are not project fixtures.

## 한국어

이 검사는 기업 공고 페이지의 짧은 발췌로 경계 사례를 살펴본 것입니다.
정확도 통계가 아닙니다. 공고는 수정되거나 마감될 수 있으므로 지원 전에는
원문을 다시 확인해야 합니다.

| 기업 공고 | 확인한 문구 유형 | 관찰 결과 |
| --- | --- | --- |
| [Nearform](https://job-boards.greenhouse.io/nearform/jobs/7619114003) | 일반 비자 지원 거절 | 비자 스폰서십 `no`, 나머지 `unknown` |
| [RoboForce](https://job-boards.greenhouse.io/roboforce/jobs/5290821008) | 조건부 이민 지원 | 비자 스폰서십·영주권 `yes`, H-1B `unknown` |
| [Cloudflare](https://job-boards.greenhouse.io/cloudflare/jobs/8199958) | 지원자에게 CPT/OPT 여부를 묻는 질문 | CPT·OPT `unknown` |
| [FORTUNE](https://boards.greenhouse.io/embed/job_app?token=5424161004) | STEM OPT·H-1B·영주권을 언급한 지원서 질문 | 세 항목 모두 `unknown` |
| [ID.me](https://job-boards.greenhouse.io/idmeuniversityrecruiting/jobs/7980382003) | E-Verify 참여 문구 | STEM OPT `unknown` |
| [Adyen](https://job-boards.greenhouse.io/adyen/jobs/8128101) | 비자 이전은 지원, 신규 H-1B CAP 청원은 거절 | 지원 범위가 갈려 H-1B·일반 비자 스폰서십 `unknown` |

[Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html)는 별도 인증
없이 Nearform 공고 전체를 반환했습니다. 전체 공고 분석에서도 비자
스폰서십 `no`와 원문 근거가 나왔습니다. API의 `content`에는 이스케이프된
HTML이 포함되어 있어 태그 제거 전에 HTML 이스케이프를 풀어야 했습니다.
첫 변환에서는 이 과정이 빠져 근거 문장에 태그가 남았습니다. 현재 분석기는
일반 텍스트만 받으며 API 수집·HTML 변환은 다음 구현 단계입니다.

여섯 발췌는 각 공고의 일부만 담았습니다. 특정 문구의 분류를 확인한
것이며 제목·기술·경력 추출의 전체 정확도를 평가한 것은 아닙니다.
검사에 쓴 임시 사본은 Git에서 제외된 `data/results/`에 있습니다.
