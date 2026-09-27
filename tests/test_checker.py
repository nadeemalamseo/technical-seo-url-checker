import unittest
from unittest.mock import Mock

import requests

from seo_url_checker import check_url, normalize_url


class TestNormalizeUrl(unittest.TestCase):
    def test_removes_default_port_and_fragment(self):
        self.assertEqual(
            normalize_url("HTTPS://Example.com:443/path#section"),
            "https://example.com/path",
        )

    def test_preserves_non_default_port(self):
        self.assertEqual(
            normalize_url("https://Example.com:8443/path"),
            "https://example.com:8443/path",
        )


class TestCheckUrl(unittest.TestCase):
    def make_response(
        self,
        *,
        status=200,
        url="https://example.com/",
        body="",
        headers=None,
        history=None,
        reason="OK",
    ):
        response = Mock(spec=requests.Response)
        response.status_code = status
        response.url = url
        response.text = body
        response.headers = requests.structures.CaseInsensitiveDict(headers or {})
        response.history = history or []
        response.reason = reason
        return response

    def test_extracts_page_level_signals(self):
        html = """
        <html><head>
          <title>Example page</title>
          <meta name="description" content="A useful description">
          <meta name="robots" content="index, follow">
          <link rel="canonical" href="https://example.com/">
        </head><body>Hello</body></html>
        """
        session = Mock()
        session.get.return_value = self.make_response(
            url="https://example.com/",
            body=html,
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

        report = check_url("https://example.com/", session=session)

        self.assertEqual(report["status_code"], 200)
        self.assertEqual(report["title"], "Example page")
        self.assertEqual(report["meta_description"], "A useful description")
        self.assertEqual(report["meta_robots"], ["index", "follow"])
        self.assertEqual(report["canonical_url"], "https://example.com/")
        self.assertTrue(report["canonical_matches_final_url"])

    def test_detects_multiple_canonicals_and_noindex(self):
        html = """
        <html><head>
          <meta name="robots" content="noindex, nofollow">
          <link rel="canonical" href="/one">
          <link rel="canonical" href="/two">
        </head></html>
        """
        session = Mock()
        session.get.return_value = self.make_response(
            url="https://example.com/final",
            body=html,
            headers={
                "Content-Type": "text/html",
                "X-Robots-Tag": "googlebot: noindex",
            },
        )

        report = check_url("https://example.com/start", session=session)

        self.assertEqual(report["canonical_count"], 2)
        self.assertIn("Multiple canonical link elements were found.", report["signals"])
        self.assertIn("noindex", report["meta_robots"])
        self.assertIn("noindex", report["x_robots_tag"])
        self.assertIn(
            "A noindex directive was observed in page or response directives.",
            report["signals"],
        )

    def test_records_redirect_chain_and_http_to_https_upgrade(self):
        redirect = self.make_response(
            status=301,
            url="http://example.com/",
            headers={"Location": "https://example.com/"},
            reason="Moved Permanently",
        )
        session = Mock()
        session.get.return_value = self.make_response(
            url="https://example.com/",
            body="<html><head><title>Example</title></head></html>",
            headers={"Content-Type": "text/html"},
            history=[redirect],
        )

        report = check_url("http://example.com/", session=session)

        self.assertEqual(report["redirect_count"], 1)
        self.assertTrue(report["http_to_https_redirect"])
        self.assertEqual(report["redirect_chain"][0]["status_code"], 301)

    def test_invalid_url_is_reported(self):
        report = check_url("example.com")
        self.assertIn("error", report)

    def test_network_failure_is_reported(self):
        session = Mock()
        session.get.side_effect = requests.ConnectionError("offline")

        report = check_url("https://example.com/", session=session)

        self.assertEqual(report["error"], "Request failed: offline")


if __name__ == "__main__":
    unittest.main()
