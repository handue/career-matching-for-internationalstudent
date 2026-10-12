"""Find ATS boards with DDGS and verify them through ATS APIs. / DDGS로 ATS 게시판을 찾고 ATS API로 확인합니다."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote, urlparse
from urllib.error import HTTPError, URLError

from ddgs import DDGS

from job_pipeline.paths import DEFAULT_CONFIG, DISCOVERED_CONFIG, DEFAULT_QUERY_CONFIG, DEFAULT_PROFILE_CONFIG
from job_pipeline.collection import (
    read_boards,
    json_get,
    us_location,
)
from job_pipeline.discovery.queries import load_profile, plan_queries

MIN_NEW_BOARDS = 2
BOARD_PATTERN = re.compile(r"[A-Za-z0-9_-]+")
# complie = save this regax in BOARD_PATTERN. we can re-use after now.


def board_from_url(url: str) -> tuple[str, str] | None:
    """Extract an ATS board from a DDGS result URL. / DDGS 검색 결과 URL에서 ATS 게시판을 추출합니다."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    host = parsed.hostname.lower()
    if host in {"job-boards.greenhouse.io", "boards.greenhouse.io"}:
        provider = "greenhouse"
    elif host == "jobs.lever.co":
        provider = "lever"
    elif host == "jobs.ashbyhq.com":
        provider = "ashby"
    elif host in {"jobs.smartrecruiters.com", "careers.smartrecruiters.com"}:
        provider = "smartrecruiters"
    else:
        return None
    board = parts[0]
    return (provider, board) if BOARD_PATTERN.fullmatch(board) else None


def board_has_us_jobs(provider: str, board: str) -> bool:
    """Check a discovered board through its public ATS API for US jobs. / 발견한 게시판의 공개 ATS API에서 미국 공고를 확인합니다."""
    slug = quote(board, safe="")
    if provider == "greenhouse":
        payload = json_get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
        jobs = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(jobs, list):
            return False
        for job in jobs:
            if isinstance(job, dict):
                location = job.get("location")
                name = location.get("name") if isinstance(location, dict) else None
                if isinstance(name, str) and us_location(name):
                    return True
        return False
    if provider == "lever":
        payload = json_get(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        if not isinstance(payload, list):
            return False
        for job in payload:
            if isinstance(job, dict):
                categories = job.get("categories")
                location = (
                    categories.get("location") if isinstance(categories, dict) else None
                )
                country = job.get("country")
                if isinstance(location, str) and us_location(
                    location, country if isinstance(country, str) else None
                ):
                    return True
        return False
    if provider == "ashby":
        payload = json_get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
        jobs = payload.get("jobs") if isinstance(payload, dict) else None
        if not isinstance(jobs, list):
            return False
        for job in jobs:
            if isinstance(job, dict) and job.get("isListed") is not False:
                location = job.get("location")
                address = job.get("address")
                postal = (
                    address.get("postalAddress", address)
                    if isinstance(address, dict)
                    else None
                )
                country = (
                    postal.get("addressCountry") if isinstance(postal, dict) else None
                )
                if isinstance(location, str) and us_location(
                    location, country if isinstance(country, str) else None
                ):
                    return True
        return False
    if provider == "smartrecruiters":
        payload = json_get(
            f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?country=US&limit=1"
        )
        jobs = payload.get("content") if isinstance(payload, dict) else None
        return isinstance(jobs, list) and len(jobs) > 0
    return False


def load_queries(path: Path) -> list[str]:
    """Load local fallback queries when Ollama planning fails. / Ollama 검색어 생성이 실패하면 로컬 예비 검색어를 읽습니다."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not 1 <= len(data) <= 20:
        raise ValueError("Discovery queries must be a JSON array with 1-20 entries")
    queries: list[str] = []
    for value in data:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Each discovery query must be a nonempty string")
        queries.append(value.strip())
    return queries


def discover_boards(
    config_path: Path, per_query: int, max_probes: int | None, queries: list[str]
) -> tuple[int, int]:
    """Search with DDGS, verify via ATS APIs, then save boards locally. / DDGS로 검색하고 ATS API로 확인한 게시판을 로컬에 저장합니다."""
    manual = read_boards(config_path)
    discovered = read_boards(DISCOVERED_CONFIG)
    known = {
        (item["provider"].lower(), item["board"].lower())
        for item in (manual + discovered)
    }
    # conbined manual + discovered and maked it to 'set'
    added = 0
    probed = 0
    failed_queries = 0
    for query in queries:
        if max_probes is not None and probed >= max_probes:
            break
        try:
            results = DDGS().text(
                query, region="us-en", max_results=per_query, backend="auto"
            )
        except Exception as error:
            failed_queries += 1
            print(f"Discovery query failed: {error}", file=sys.stderr)
            continue
        for result in results:
            if max_probes is not None and probed >= max_probes:
                break
            href = result.get("href")
            candidate = board_from_url(href) if isinstance(href, str) else None
            if candidate is None:
                continue
            provider, board = candidate
            key = (provider, board.lower())
            if key in known:
                continue
            known.add(key)
            probed += 1
            try:
                valid = board_has_us_jobs(provider, board)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                print(
                    f"Board check failed: {provider}/{board}: {error}", file=sys.stderr
                )
                continue
            if not valid:
                print(
                    f"Skipped board without confirmed US postings: {provider}/{board}"
                )
                continue
            discovered.append({"provider": provider, "board": board})
            added += 1
            print(f"Discovered board: {provider}/{board}")
    DISCOVERED_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    DISCOVERED_CONFIG.write_text(
        json.dumps(discovered, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"New boards: {added}, API checks: {probed}, failed queries: {failed_queries}, saved boards: {len(discovered)}"
    )
    return added, probed


def discover_adaptively(
    config_path: Path,
    per_query: int,
    max_probes: int | None,
    fallback_path: Path,
    profile_path: Path,
    model: str,
) -> tuple[int, int]:
    """Use Ollama queries for DDGS; retry once and fall back to local queries. / Ollama 검색어로 DDGS를 실행하고 한 번 재검색하거나 로컬 검색어로 대체합니다."""
    try:
        profile = load_profile(profile_path)
        queries = plan_queries(profile, model)
        print("Ollama generated discovery queries:")
        for query in queries:
            print(f"  {query}")
    except (
        HTTPError,
        URLError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        print(
            f"Ollama query planning failed: {error}. Using fallback queries.",
            file=sys.stderr,
        )
        return discover_boards(
            config_path, per_query, max_probes, load_queries(fallback_path)
        )

    added, probed = discover_boards(config_path, per_query, max_probes, queries)
    if added >= MIN_NEW_BOARDS or (max_probes is not None and probed >= max_probes):
        return added, probed
    try:
        revised = plan_queries(profile, model, previous=queries)
        print("Ollama revised discovery queries:")
        for query in revised:
            print(f"  {query}")
    except (
        HTTPError,
        URLError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        print(
            f"Ollama query revision failed: {error}. Using fallback queries.",
            file=sys.stderr,
        )
        revised = [
            query for query in load_queries(fallback_path) if query not in queries
        ]
    if not revised:
        return added, probed
    remaining = None if max_probes is None else max_probes - probed
    retry_added, retry_probed = discover_boards(config_path, per_query, remaining, revised)
    return added + retry_added, probed + retry_probed


def main() -> int:
    """Run ATS discovery from CLI arguments. / 명령행 인자로 ATS 게시판 발견을 실행합니다."""
    parser = argparse.ArgumentParser(
        description="Discover public ATS boards with US postings."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Manual ATS board configuration",
    )
    parser.add_argument(
        "--queries-file",
        type=Path,
        default=DEFAULT_QUERY_CONFIG,
        help="Discovery query configuration",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE_CONFIG,
        help="Search profile for Ollama query planning",
    )
    parser.add_argument(
        "--model", default="qwen3:8b", help="Ollama model for search queries"
    )
    parser.add_argument(
        "--per-query", type=int, default=5, help="Maximum DDGS results per query (1-10)"
    )
    parser.add_argument(
        "--max-probes", type=int, help="Optional maximum ATS API checks"
    )
    args = parser.parse_args()
    if not 1 <= args.per_query <= 10 or (args.max_probes is not None and args.max_probes < 1):
        parser.error("--per-query must be 1-10 and --max-probes, if set, must be positive")
    try:
        discover_adaptively(
            args.config,
            args.per_query,
            args.max_probes,
            args.queries_file,
            args.profile,
            args.model,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Board discovery failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
