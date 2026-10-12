"""Collect public ATS postings. / 공개 ATS 공고를 수집합니다."""

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import time
from typing import TypedDict
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


from job_pipeline.paths import ROOT, DEFAULT_CONFIG, DISCOVERED_CONFIG
OUTPUT_DIR = ROOT / "data" / "results" / "ats_collection"
PROVIDERS = {"greenhouse", "lever", "ashby", "smartrecruiters"}
MAX_RESPONSE_BYTES = 5_000_000
MAX_429_ATTEMPTS = 3
MAX_RETRY_WAIT_SECONDS = 30
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
    "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
    "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
    "WV", "WI", "WY",
}


class Posting(TypedDict):
    url: str
    title: str
    company: str
    location: str
    content: str
    posted_at: str | None


def retry_after_seconds(value: str | None, attempt: int) -> float:
    """Read 429 Retry-After or use a short backoff. / 429의 Retry-After를 읽거나 짧게 점증 대기합니다."""
    if value is None:
        return float(2 ** attempt)
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid Retry-After header: {value}") from error
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())


def json_get(url: str) -> object:
    """Read ATS JSON; retry 429 up to three attempts. / ATS JSON을 읽고 429는 최대 세 번 시도합니다."""
    request = Request(url, headers={"User-Agent": "career-match/0.1", "Accept": "application/json"})
    for attempt in range(MAX_429_ATTEMPTS):
        try:
            with urlopen(request, timeout=20) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("ATS response exceeds 5 MB")
            return json.loads(raw)
        except HTTPError as error:
            if error.code != 429 or attempt == MAX_429_ATTEMPTS - 1:
                raise
            delay = retry_after_seconds(error.headers.get("Retry-After"), attempt)
            if delay > MAX_RETRY_WAIT_SECONDS:
                raise ValueError(
                    f"ATS requested a {delay:.0f}s retry wait; skipped this board"
                ) from error
            print(f"ATS rate limited (429); retrying in {delay:g}s (attempt {attempt + 2}/{MAX_429_ATTEMPTS})")
            time.sleep(delay)
    raise RuntimeError("ATS request retries exhausted")


def plain_text(value: str) -> str:
    """Remove markup from a public description. / 공개 공고 본문에서 HTML을 제거합니다."""
    for _ in range(2):
        value = html.unescape(value)
    soup = BeautifulSoup(value, "html.parser")
    return "\n".join(line for line in (part.strip() for part in soup.get_text("\n").splitlines()) if line)


def us_location(location: str, country: str | None = None) -> bool:
    """Accept explicit US evidence only. / 미국이라는 명시적 근거가 있을 때만 받습니다."""
    if country:
        return country.upper() in {"US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"}
    if re.search(r"\b(?:United States|USA|U\.S\.|US)\b", location, re.IGNORECASE):
        return True
    state = re.search(r",\s*([A-Z]{2})(?:\b|$)", location)
    return bool(state and state.group(1) in US_STATES)


def greenhouse(board: str) -> list[Posting]:
    payload = json_get(f"https://boards-api.greenhouse.io/v1/boards/{quote(board)}/jobs?content=true")
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("Invalid Greenhouse job list")
    postings: list[Posting] = []
    for raw in payload["jobs"]:
        if not isinstance(raw, dict) or raw.get("internal_job_id") is None:
            continue
        location_data = raw.get("location")
        location = location_data.get("name", "") if isinstance(location_data, dict) else ""
        if not isinstance(location, str) or not us_location(location):
            continue
        title, url, content = raw.get("title"), raw.get("absolute_url"), raw.get("content")
        if not isinstance(title, str) or not isinstance(url, str) or not isinstance(content, str):
            continue
        company = raw.get("company_name")
        first_published = raw.get("first_published")
        postings.append({
            "url": url,
            "title": title,
            "company": company.strip() if isinstance(company, str) else board,
            "location": location,
            "content": content,
            "posted_at": first_published if isinstance(first_published, str) else None,
        })
    return postings


def lever(board: str) -> list[Posting]:
    payload = json_get(f"https://api.lever.co/v0/postings/{quote(board)}?mode=json")
    if not isinstance(payload, list):
        raise ValueError("Invalid Lever job list")
    postings: list[Posting] = []
    for raw in payload:
        if not isinstance(raw, dict):
            continue
        categories = raw.get("categories")
        location = categories.get("location", "") if isinstance(categories, dict) else ""
        country = raw.get("country")
        if not isinstance(location, str) or not us_location(location, country if isinstance(country, str) else None):
            continue
        title, url = raw.get("text"), raw.get("hostedUrl")
        description = raw.get("descriptionPlain") or raw.get("description")
        extra_value = raw.get("additionalPlain") or raw.get("additional") or ""
        extra = extra_value if isinstance(extra_value, str) else ""
        lists = raw.get("lists")
        if isinstance(lists, list):
            extra += "\n" + "\n".join(str(item.get("content", "")) for item in lists if isinstance(item, dict))
        if not isinstance(title, str) or not isinstance(url, str) or not isinstance(description, str):
            continue
        postings.append({"url": url, "title": title, "company": board, "location": location, "content": description + "\n" + extra, "posted_at": None})
    return postings


def ashby(board: str) -> list[Posting]:
    payload = json_get(f"https://api.ashbyhq.com/posting-api/job-board/{quote(board)}")
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise ValueError("Invalid Ashby job list")
    postings: list[Posting] = []
    for raw in payload["jobs"]:
        if not isinstance(raw, dict) or raw.get("isListed") is False:
            continue
        location = raw.get("location")
        address = raw.get("address")
        postal = address.get("postalAddress", address) if isinstance(address, dict) else {}
        country = postal.get("addressCountry") if isinstance(postal, dict) else None
        if not isinstance(location, str) or not us_location(location, country if isinstance(country, str) else None):
            continue
        title, url = raw.get("title"), raw.get("jobUrl")
        description = raw.get("descriptionPlain") or raw.get("descriptionHtml")
        if not isinstance(title, str) or not isinstance(url, str) or not isinstance(description, str):
            continue
        posted = raw.get("publishedAt")
        postings.append({"url": url, "title": title, "company": board, "location": location, "content": description, "posted_at": posted if isinstance(posted, str) else None})
    return postings


def smartrecruiters(board: str) -> list[Posting]:
    postings: list[Posting] = []
    offset = 0
    # Bound detail requests during this first integration. / 초기 연동에서는 상세 조회 횟수를 제한합니다.
    while offset < 100:
        payload = json_get(f"https://api.smartrecruiters.com/v1/companies/{quote(board)}/postings?country=US&limit=100&offset={offset}")
        if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
            raise ValueError("Invalid SmartRecruiters job list")
        jobs = payload["content"]
        for raw in jobs:
            if not isinstance(raw, dict):
                continue
            location_data = raw.get("location")
            if not isinstance(location_data, dict) or str(location_data.get("country", "")).upper() != "US":
                continue
            posting_id = raw.get("id")
            if not isinstance(posting_id, (str, int)):
                continue
            details = json_get(f"https://api.smartrecruiters.com/v1/companies/{quote(board)}/postings/{quote(str(posting_id))}")
            if not isinstance(details, dict):
                continue
            title = details.get("name")
            url = details.get("applyUrl")
            job_ad = details.get("jobAd")
            sections = job_ad.get("sections") if isinstance(job_ad, dict) else None
            content = "\n".join(str(section.get("text", "")) for section in sections.values() if isinstance(section, dict)) if isinstance(sections, dict) else ""
            if not isinstance(title, str) or not isinstance(url, str) or not content:
                continue
            location = ", ".join(str(location_data.get(key)) for key in ("city", "region", "country") if location_data.get(key))
            posted = raw.get("releasedDate")
            postings.append({"url": url, "title": title, "company": board, "location": location, "content": content, "posted_at": posted if isinstance(posted, str) else None})
        offset += len(jobs)
        total = payload.get("totalFound")
        if not jobs or (isinstance(total, int) and offset >= total):
            break
    return postings


FETCHERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "smartrecruiters": smartrecruiters}


def read_boards(path: Path, *, required: bool = False) -> list[dict[str, str]]:
    """Validate board configuration for discovery and collection. / 발견・수집이 공유하는 게시판 설정을 검증합니다."""
    if not path.is_file() and not required:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Board file must be a JSON array: {path}")
    boards: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid board in {path}")
        provider, board = item.get("provider"), item.get("board")
        if not isinstance(provider, str) or not isinstance(board, str):
            raise ValueError(f"Invalid board in {path}")
        provider = provider.lower()
        if provider not in PROVIDERS or not re.fullmatch(r"[A-Za-z0-9_-]+", board):
            raise ValueError(f"Invalid ATS board: {item}")
        boards.append({"provider": provider, "board": board})
    return boards


def collect_jobs(config_path: Path, limit: int) -> tuple[Path, int, int]:
    """Write an analyzer-compatible report. / 분석기가 읽을 수 있는 보고서를 저장합니다."""
    boards = read_boards(config_path, required=True) + read_boards(DISCOVERED_CONFIG)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report: list[dict[str, str | int | bool | None]] = []
    seen: set[str] = set()
    seen_boards: set[tuple[str, str]] = set()
    board_postings: list[tuple[str, list[Posting]]] = []
    failures = 0
    for entry in boards:
        provider, board = entry["provider"], entry["board"]
        board_key = (provider, board.lower())
        if board_key in seen_boards:
            continue
        seen_boards.add(board_key)
        try:
            postings = FETCHERS[provider](board)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"Board failed: {provider}/{board}: {error}", file=sys.stderr)
            failures += 1
            continue
        print(f"Board: {provider}/{board}, US postings: {len(postings)}")
        board_postings.append((provider, postings))

    # Take one posting per board in each pass. / 순회마다 게시판별 공고를 하나씩 담습니다.
    round_index = 0
    while len(report) < limit and any(round_index < len(items) for _, items in board_postings):
        for provider, postings in board_postings:
            if len(report) >= limit or round_index >= len(postings):
                continue
            posting = postings[round_index]
            url = posting["url"]
            if not url.startswith("https://") or url in seen:
                continue
            content = plain_text(posting["content"])
            if len(content) < 500:
                continue
            seen.add(url)
            file_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
            text_path = OUTPUT_DIR / f"{file_id}.txt"
            text_path.write_text("\n".join((posting["title"], posting["company"], posting["location"], "", content)) + "\n", encoding="utf-8")
            report.append({
                "url": url, "title": posting["title"], "snippet": "", "text_file": str(text_path.relative_to(ROOT)),
                "characters": len(content), "status": "text_extracted", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                "posted_at": posting["posted_at"], "deadline_at": None, "job_candidate": True, "availability": "listed_active",
                "discovery": f"ats:{provider}",
            })
            print(f"Collected: {posting['title']} | {url}")
        round_index += 1
    report_path = OUTPUT_DIR / "latest.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Collected: {len(report)}, board failures: {failures}, report: {report_path}")
    return report_path, len(report), failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect US jobs from public ATS APIs.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="ATS board configuration")
    parser.add_argument("--limit", type=int, default=10, help="Maximum postings to save")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    try:
        _, _, failures = collect_jobs(args.config, args.limit)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ATS collection failed: {error}", file=sys.stderr)
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
