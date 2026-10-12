"""Search with DDGS and extract job page text. / DDGS로 검색하고 공고 본문을 추출합니다."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from ddgs import DDGS

from job_pipeline.paths import ROOT
OUTPUT_DIR = ROOT / "data" / "results" / "search_probe"
MAX_PAGE_BYTES = 1_000_000


class PageData(TypedDict):
    text: str
    checked_at_utc: str
    posted_at: str | None
    deadline_at: str | None
    job_candidate: bool
    availability: str


def normalized_url(value: str) -> str | None:
    """Accept public HTTP(S) URLs. / 공개 HTTP(S) 주소만 받습니다."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    if parsed.hostname in ("localhost", "127.0.0.1"):
        return None
    return parsed._replace(fragment="").geturl()


def find_job_posting(value: object) -> dict[str, object] | None:
    """Find JobPosting JSON-LD data. / JSON-LD에서 채용 공고 데이터를 찾습니다."""
    if isinstance(value, list):
        for entry in value:
            found = find_job_posting(entry)
            if found is not None:
                return found
    if isinstance(value, dict):
        kinds = value.get("@type")
        if kinds == "JobPosting" or (isinstance(kinds, list) and "JobPosting" in kinds):
            return {str(key): item for key, item in value.items()}
        for key in ("@graph", "mainEntity"):
            found = find_job_posting(value.get(key))
            if found is not None:
                return found
    return None


def fetch_page(url: str) -> PageData:
    """Fetch text and available job dates. / 본문과 공개된 공고 날짜를 가져옵니다."""
    request = Request(url, headers={"User-Agent": "career-match/0.1"})
    with urlopen(request, timeout=15) as response:
        content_type = response.headers.get_content_type()
        if content_type != "text/html":
            raise ValueError(f"Expected HTML, received {content_type}")
        raw = response.read(MAX_PAGE_BYTES + 1)
        # response.read = getting bytes data from server as much as (n). in this case, it's MAX_PAGE_BYTES + 1
        if len(raw) > MAX_PAGE_BYTES:
            # len(raw) counts downloaded bytes. / 다운로드한 바이트 수를 셉니다.
            raise ValueError("Page exceeds the 1 MB probe limit")
        charset = response.headers.get_content_charset() or "utf-8"

    soup = BeautifulSoup(raw.decode(charset, errors="replace"), "html.parser")
    posting_data: dict[str, object] | None = None
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            posting_data = find_job_posting(json.loads(script.get_text()))
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if posting_data is not None:
            break
    has_heading = bool(soup.find("h1"))
    # Keep application-form questions because they may mention work authorization.
    # 지원 양식에 취업 허가 질문이 있을 수 있으므로 form은 남깁니다.
    for element in soup(("script", "style", "nav", "footer", "header")):
        element.decompose()
    lines = (line.strip() for line in soup.get_text("\n").splitlines())
    text = "\n".join(line for line in lines if line)
    posted_at = posting_data.get("datePosted") if posting_data else None
    deadline_at = posting_data.get("validThrough") if posting_data else None
    closed_phrases = (
        "no longer accepting applications",
        "this job is closed",
        "applications are closed",
    )
    availability = (
        "closed"
        if any(phrase in text.lower() for phrase in closed_phrases)
        else "accessible_unverified"
    )
    return {
        "text": text,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "posted_at": posted_at if isinstance(posted_at, str) else None,
        "deadline_at": deadline_at if isinstance(deadline_at, str) else None,
        "job_candidate": posting_data is not None or (has_heading and "apply" in text.lower()),
        "availability": availability,
    }


def search_jobs(query: str, limit: int) -> tuple[Path, int, int]:
    """Search and save candidate pages. / 공고 후보를 검색해 페이지를 저장합니다."""
    results = DDGS().text(query, region="us-en", max_results=limit, backend="auto")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    report: list[dict[str, str | int | bool | None]] = []
    for result in results:
        url = normalized_url(result.get("href", ""))
        if url is None or url in seen:
            continue
        seen.add(url)
        item: dict[str, str | int | bool | None] = {
            "url": url,
            "title": result.get("title", ""),
            "snippet": result.get("body", ""),
        }
        try:
            page = fetch_page(url)
            content = page["text"]
            text_path = (
                OUTPUT_DIR / f"{hashlib.sha256(url.encode()).hexdigest()[:16]}.txt"
            )
            text_path.write_text(content + "\n", encoding="utf-8")
            item["text_file"] = str(text_path.relative_to(ROOT))
            item["characters"] = len(content)
            item["checked_at_utc"] = page["checked_at_utc"]
            item["posted_at"] = page["posted_at"]
            item["deadline_at"] = page["deadline_at"]
            item["job_candidate"] = page["job_candidate"]
            item["availability"] = page["availability"]
            item["status"] = "text_extracted" if len(content) >= 500 else "short_text"
        except (HTTPError, URLError, OSError, ValueError, LookupError) as error:
            item["status"] = "fetch_failed"
            item["error"] = str(error)
        report.append(item)
        print(f"{item['status']}: {item['title']} | {url}")

    report_path = OUTPUT_DIR / "latest.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    extracted = sum(item["status"] == "text_extracted" for item in report)
    print(f"Results: {len(report)}, pages with extracted text: {extracted}")
    print(f"Report: {report_path}")
    return report_path, len(report), extracted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe DDGS job search and page extraction."
    )
    parser.add_argument("--query", required=True, help="Job search query")
    # Probe-only limit; tune result count against page fetch time for production.
    # 시험용 제한이며 실제 수집에서는 페이지 수와 실행 시간을 보고 조정합니다.
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum search results to inspect (1-10)"
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 10:
        parser.error("--limit must be between 1 and 10")

    try:
        search_jobs(args.query, args.limit)
    except Exception as error:
        print(f"Search failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
