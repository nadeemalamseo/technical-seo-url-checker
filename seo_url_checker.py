#!/usr/bin/env python3
"""URL-level technical SEO diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 20
DEFAULT_USER_AGENT = "TechnicalSEOURLChecker/1.0 (+https://github.com/nadeemalamseo/technical-seo-url-checker)"


def normalize_url(url: str) -> str:
    """Normalize a URL enough for comparison without changing path semantics."""
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    hostname = (parts.hostname or "").lower()
    if not hostname:
        return url.strip()
    try:
        port = parts.port
    except ValueError:
        port = None
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        netloc = hostname
    elif port:
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname
    return urlunsplit((scheme, netloc, parts.path or "/", parts.query, ""))


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = " ".join(value.split())
    return text or None


def _directives(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip().lower() for part in value.split(",") if part.strip()]


def _parse_x_robots(value: str | None) -> list[str]:
    if not value:
        return []
    directives: list[str] = []
    for segment in value.split(","):
        segment = segment.strip()
        if not segment:
            continue
        if ":" in segment:
            segment = segment.split(":", 1)[1].strip()
        directives.extend(_directives(segment))
    return directives


def check_url(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Fetch and inspect one URL, returning observable evidence."""
    requested_url = url.strip()
    if not requested_url:
        return {"url": requested_url, "error": "URL is empty."}

    parts = urlsplit(requested_url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return {
            "url": requested_url,
            "error": "URL must include an http:// or https:// scheme and a hostname.",
        }

    client = session or requests.Session()
    try:
        response = client.get(
            requested_url,
            headers={"User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml"},
            timeout=timeout,
            allow_redirects=True,
        )
    except requests.TooManyRedirects:
        return {"url": requested_url, "error": "Too many redirects."}
    except requests.RequestException as exc:
        return {"url": requested_url, "error": f"Request failed: {exc}"}

    final_url = response.url
    content_type = response.headers.get("Content-Type", "")
    is_html = "html" in content_type.lower()

    result: dict[str, Any] = {
        "url": requested_url,
        "status_code": response.status_code,
        "reason": response.reason,
        "final_url": final_url,
        "redirect_count": len(response.history),
        "redirect_chain": [
            {"status_code": item.status_code, "from": item.url, "to": item.headers.get("Location")}
            for item in response.history
        ],
        "content_type": content_type or None,
        "is_html": is_html,
        "https_final": urlsplit(final_url).scheme.lower() == "https",
        "http_to_https_redirect": (
            urlsplit(requested_url).scheme.lower() == "http"
            and urlsplit(final_url).scheme.lower() == "https"
        ),
        "title": None,
        "meta_description": None,
        "meta_robots": [],
        "x_robots_tag": [],
        "canonical_urls": [],
        "canonical_count": 0,
        "canonical_url": None,
        "canonical_matches_final_url": None,
        "signals": [],
    }

    if not is_html:
        result["signals"].append(
            "Response is not identified as HTML; page-level HTML checks were skipped."
        )
        return result

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    result["title"] = _clean_text(title.get_text(" ", strip=True) if title else None)

    description = soup.find(
        "meta",
        attrs={"name": lambda value: isinstance(value, str) and value.lower() == "description"},
    )
    result["meta_description"] = _clean_text(
        description.get("content") if description else None
    )

    robots_values = [
        tag.get("content", "")
        for tag in soup.find_all(
            "meta",
            attrs={"name": lambda value: isinstance(value, str) and value.lower() == "robots"},
        )
    ]
    result["meta_robots"] = [
        directive for value in robots_values for directive in _directives(value)
    ]

    result["x_robots_tag"] = _parse_x_robots(response.headers.get("X-Robots-Tag"))

    canonical_tags = soup.find_all(
        "link",
        attrs={
            "rel": lambda value: (
                isinstance(value, list)
                and any(str(item).lower() == "canonical" for item in value)
            )
            or (isinstance(value, str) and "canonical" in value.lower())
        },
    )
    canonical_urls = []
    for tag in canonical_tags:
        href = (tag.get("href") or "").strip()
        if href:
            canonical_urls.append(urljoin(final_url, href))

    result["canonical_urls"] = canonical_urls
    result["canonical_count"] = len(canonical_urls)
    result["canonical_url"] = canonical_urls[0] if canonical_urls else None
    if canonical_urls:
        result["canonical_matches_final_url"] = (
            normalize_url(canonical_urls[0]) == normalize_url(final_url)
        )

    if not canonical_urls:
        result["signals"].append("No canonical link element was found.")
    elif len(canonical_urls) > 1:
        result["signals"].append("Multiple canonical link elements were found.")
    if result["canonical_matches_final_url"] is False:
        result["signals"].append("The first canonical URL differs from the final fetched URL.")

    if "noindex" in result["meta_robots"] or "noindex" in result["x_robots_tag"]:
        result["signals"].append("A noindex directive was observed in page or response directives.")
    if "nofollow" in result["meta_robots"] or "nofollow" in result["x_robots_tag"]:
        result["signals"].append("A nofollow directive was observed in page or response directives.")
    if result["redirect_count"] > 1:
        result["signals"].append("More than one redirect was observed.")
    if response.status_code >= 400:
        result["signals"].append("The final HTTP response is an error status.")
    if not result["title"]:
        result["signals"].append("No non-empty title element was found.")
    if not result["meta_description"]:
        result["signals"].append("No non-empty meta description was found.")

    return result


def print_report(report: dict[str, Any]) -> None:
    if "error" in report:
        print(f"URL: {report.get('url', '')}")
        print(f"Error: {report['error']}")
        return

    print(f"URL: {report['url']}")
    print(f"Status: {report['status_code']} {report['reason'] or ''}".rstrip())
    print(f"Final URL: {report['final_url']}")
    print(f"Redirects: {report['redirect_count']}")
    print(f"Content-Type: {report['content_type'] or '—'}")
    print(f"HTML: {'yes' if report['is_html'] else 'no'}")
    print(f"HTTPS final: {'yes' if report['https_final'] else 'no'}")
    print(f"HTTP → HTTPS: {'yes' if report['http_to_https_redirect'] else 'no'}")

    if report["is_html"]:
        print(f"Title: {report['title'] or '—'}")
        print(f"Meta Description: {report['meta_description'] or '—'}")
        print(f"Meta Robots: {', '.join(report['meta_robots']) or '—'}")
        print(f"X-Robots-Tag: {', '.join(report['x_robots_tag']) or '—'}")
        print(f"Canonical: {report['canonical_url'] or '—'}")
        if report["canonical_count"] > 1:
            print(f"Canonical Count: {report['canonical_count']}")

    if report["redirect_chain"]:
        print("Redirect Chain:")
        for item in report["redirect_chain"]:
            print(
                f"  {item['status_code']}: {item['from']} -> "
                f"{item['to'] or '(missing Location)'}"
            )

    if report["signals"]:
        print("Signals:")
        for signal in report["signals"]:
            print(f"  - {signal}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check URL-level HTTP and technical SEO signals."
    )
    parser.add_argument("urls", nargs="+", help="One or more HTTP(S) URLs to check.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT}).",
    )
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="Custom User-Agent.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero.")

    session = requests.Session()
    reports = [
        check_url(url, timeout=args.timeout, user_agent=args.user_agent, session=session)
        for url in args.urls
    ]

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        for index, report in enumerate(reports):
            if index:
                print("\n" + ("-" * 60) + "\n")
            print_report(report)

    return 0 if all("error" not in report for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
