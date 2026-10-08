"""Probe job search and page text extraction. / 공고 검색과 원문 추출을 시험합니다."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    from bs4 import BeautifulSoup
    from ddgs import DDGS
except ImportError as error:
    print(f"Missing dependency: {error}. Install ddgs and beautifulsoup4.", file=sys.stderr)
    raise SystemExit(1) from error


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "results" / "search_probe"
MAX_PAGE_BYTES = 1_000_000


def normalized_url(value: str) -> str | None:
    """Accept public HTTP(S) URLs. / 공개 HTTP(S) 주소만 받습니다."""
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    if parsed.hostname in ("localhost", "127.0.0.1"):
        return None
    return parsed._replace(fragment="").geturl()


def page_text(url: str) -> str:
    """Fetch and clean visible HTML text. / HTML의 보이는 텍스트를 가져옵니다."""
    request = Request(url, headers={"User-Agent": "career-match/0.1"})
    with urlopen(request, timeout=15) as response:
        content_type = response.headers.get_content_type()
        if content_type != "text/html":
            raise ValueError(f"Expected HTML, received {content_type}")
        raw = response.read(MAX_PAGE_BYTES + 1)
        if len(raw) > MAX_PAGE_BYTES:
            raise ValueError("Page exceeds the 1 MB probe limit")
        charset = response.headers.get_content_charset() or "utf-8"

    soup = BeautifulSoup(raw.decode(charset, errors="replace"), "html.parser")
    for element in soup(("script", "style", "nav", "footer", "header", "form")):
        element.decompose()
    lines = (line.strip() for line in soup.get_text("\n").splitlines())
    return "\n".join(line for line in lines if line)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe DDGS job search and page extraction."
    )
    parser.add_argument("--query", required=True, help="Job search query")
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum search results to inspect (1-10)"
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 10:
        parser.error("--limit must be between 1 and 10")

    try:
        results = DDGS().text(
            args.query, region="us-en", max_results=args.limit, backend="auto"
        )
    except Exception as error:
        print(f"Search failed: {error}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    report: list[dict[str, str | int]] = []
    for result in results:
        url = normalized_url(result.get("href", ""))
        if url is None or url in seen:
            continue
        seen.add(url)
        item: dict[str, str | int] = {
            "url": url,
            "title": result.get("title", ""),
            "snippet": result.get("body", ""),
        }
        try:
            content = page_text(url)
            text_path = (
                OUTPUT_DIR / f"{hashlib.sha256(url.encode()).hexdigest()[:16]}.txt"
            )
            text_path.write_text(content + "\n", encoding="utf-8")
            item["text_file"] = str(text_path.relative_to(ROOT))
            item["characters"] = len(content)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
