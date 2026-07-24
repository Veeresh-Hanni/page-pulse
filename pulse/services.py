from __future__ import annotations

import re
import socket
import time
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class UrlValidationError(ValueError):
    pass


class FetchError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(message)


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.meta_description = ""
        self.h1_count = 0
        self.images_missing_alt = 0
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.meta_description = (attrs_dict.get("content") or "").strip()
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "img":
            alt = attrs_dict.get("alt")
            if alt is None or alt.strip() == "":
                self.images_missing_alt += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        self.text_chunks.append(data)


def validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise UrlValidationError("URL must include http:// or https:// and a valid host.")


def fetch_url(url: str, timeout_seconds: float = 8.0) -> dict[str, Any]:
    request = Request(url=url, headers={"User-Agent": "PagePulse/1.0"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read()
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return {
                "status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "body": body,
                "response_time_ms": elapsed_ms,
            }
    except HTTPError as error:
        body = error.read()
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "status": error.code,
            "content_type": error.headers.get("Content-Type", ""),
            "body": body,
            "response_time_ms": elapsed_ms,
        }
    except TimeoutError as error:
        raise FetchError("Timed out while fetching URL.", 504) from error
    except URLError as error:
        if isinstance(error.reason, (TimeoutError, socket.timeout)):
            raise FetchError("Timed out while fetching URL.", 504) from error
        raise FetchError("Could not fetch URL.", 502) from error


def parse_html_metrics(html: str) -> dict[str, Any]:
    if not isinstance(html, str):
        raise TypeError("HTML content must be a string.")
    if html.strip() == "":
        raise ValueError("HTML content is empty.")

    parser = _PageParser()
    parser.feed(html)
    parser.close()

    text_content = " ".join(parser.text_chunks)
    words = re.findall(r"\b[\w'-]+\b", text_content)

    return {
        "page_title": "".join(parser.title_parts).strip(),
        "meta_description": parser.meta_description,
        "h1_count": parser.h1_count,
        "images_missing_alt": parser.images_missing_alt,
        "approx_word_count": len(words),
    }
