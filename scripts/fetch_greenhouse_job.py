"""Fetch one Greenhouse posting as plain text. / Greenhouse 공고 하나를 일반 텍스트로 저장합니다."""

import argparse
from datetime import datetime, timezone
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from job_record import SourceMetadata

ROOT: Path = Path(__file__).resolve().parents[1]
BLOCK_TAGS: set[str] = {"p", "div", "li", "br", "h1", "h2", "h3", "ul", "ol"}


# HTMLParser subclass to extract text and line breaks from HTML content.
# HTMLParser 는 이미 파이썬에 있는 HTML 읽기 도구. 근데 우리 이거 받아와서, 태그 만나면 줄바꿈 넣고 글자 만나면 저장하는 규칙 추가.
class PostingHTMLParser(HTMLParser):
    """Keep text and line breaks from HTML. / HTML의 텍스트와 줄바꿈을 보존합니다."""

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(content: str) -> str:
    """Decode escaped markup and remove tags. / 이스케이프를 풀고 HTML 태그를 제거합니다."""
    for _ in range(2):
        content = html.unescape(content)
    parser = PostingHTMLParser()
    parser.feed(content)

    # if line.strip() = execute line.strip() and return the result if it's not empty. If it is empty, skip it.
    # Split text into lines, remove blank lines, and trim whitespace.

    # 텍스트를 줄별로 나누고 빈 줄과 앞뒤 공백을 제거합니다. 연속된 줄바꿈 사이에는 빈 줄이 생깁니다.
    # ex) text = "Hello \n\n World", text.splitlines() => ["Hello", "", "world"] (참고로 \n이 두 개여야 "" 생기고, 하나면 그냥 사라짐)
    # 그래서 \n이 두 개인 경우, 리스트에 ""가 생기기에 마지막 if line.strip()으로 다시 검증해서 빈 문자열은 안나가게끔 하는거
    # 대신 그렇게 정리한거에 마지막에 줄바꿈 하면서 나중에 가독성 좋게 하는거

    # "" is always false in Python
    return "\n".join(
        line.strip() for line in "".join(parser.parts).splitlines() if line.strip()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Save one public Greenhouse job posting as plain text."
    )
    parser.add_argument(
        "--board", required=True, help="Greenhouse board token, such as nearform"
    )
    parser.add_argument(
        "--job-id", required=True, type=int, help="Public Greenhouse job post ID"
    )
    args = parser.parse_args()

    # '+'  = 앞의 허용문자들이 한 글자 이상 있어야함. 걍 글자가 ""처럼 비어있는지, !나 공백이 있는지 체크하는거 같은데
    # fullmatch = 문자열의 모든 글자가 조건식에 허용된 글자여야한다
    # 즉 여기서 fullmatch 랑 + 는 허용된 글자가 최소 하나 있어야 하고, 문자열의 모든 글자가 허용된 글자여야 한다는 뜻.
    # r = raw string
    # A-Za-z0-9_- => 영어 대/소문자,숫자,밑줄,하이픈 - 중 한 글 자
    # 이거 Not은 괄호 안 돼있어서 앞에만 적용된거야

    # check if args.board fulfill regax '[A-Za-z0-9_-]+'
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.board) or args.job_id <= 0:
        print("Invalid board token or job ID.", file=sys.stderr)
        return 1

    api_url = (
        f"https://boards-api.greenhouse.io/v1/boards/{args.board}/jobs/{args.job_id}"
    )
    request = Request(api_url, headers={"User-Agent": "career-match/0.1"})
    try:
        with urlopen(request, timeout=30) as response:
            job = json.load(response)
        title = job["title"]
        company = job["company_name"]
        location = job["location"]["name"]
        source_url = job["absolute_url"]
        content = job["content"]
        if not all(
            isinstance(value, str)
            for value in (title, company, location, source_url, content)
        ):
            raise ValueError("Unexpected job field types")
        description = html_to_text(content)
        if not description:
            raise ValueError("Empty job description")
        posting = "\n".join((title, company, location, "", description)) + "\n"
        output = (
            ROOT / "data" / "results" / "greenhouse" / args.board / f"{args.job_id}.txt"
        )
        # Create the output directory and any missing parents. / 누락된 상위 폴더까지 만듭니다.
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_text(posting, encoding="utf-8")
        metadata: SourceMetadata = {
            "source_url": source_url,
            "board": args.board,
            "job_id": args.job_id,
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        output.with_suffix(".json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
    except HTTPError as error:
        print("Greenhouse HTTP error {}.".format(error.code), file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError) as error:
        print("Cannot fetch or save the posting: {}".format(error), file=sys.stderr)
        return 1
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print("Invalid Greenhouse response: {}".format(error), file=sys.stderr)
        return 1

    print("Saved posting: {}".format(output))
    print("Saved metadata: {}".format(output.with_suffix(".json")))
    print("Original posting: {}".format(source_url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
