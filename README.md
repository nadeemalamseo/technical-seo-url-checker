# Technical SEO URL Checker

A practical URL-level technical SEO checker for HTTP status, redirects, canonical tags, robots directives, and basic indexability signals.

## What it checks

- HTTP status and final URL
- Redirect count and redirect chain
- Content type
- HTML title and meta description
- Meta robots directives
- `X-Robots-Tag` response directives
- Canonical URL presence and multiplicity
- Canonical-to-final-URL comparison
- HTTP-to-HTTPS upgrade
- Basic evidence that may affect URL-level technical SEO review

The checker reports **observable page and HTTP evidence**. It does not claim to know whether a search engine has indexed a URL, which canonical a search engine selected, or how a page will rank.

## Requirements

- Python 3.10+
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Check one URL:

```bash
python seo_url_checker.py https://example.com/
```

Return machine-readable JSON:

```bash
python seo_url_checker.py https://example.com/ --json
```

Set a request timeout:

```bash
python seo_url_checker.py https://example.com/ --timeout 15
```

Check several URLs:

```bash
python seo_url_checker.py https://example.com/ https://example.com/about/
```

## Example output

Human-readable output is intentionally compact:

```text
URL: https://example.com/
Status: 200
Final URL: https://example.com/
Redirects: 0
Content-Type: text/html
Title: Example
Meta Description: Example description
Canonical: https://example.com/
Meta Robots: index, follow
X-Robots-Tag: —
```

The JSON output contains the same evidence in a structured form for audits or downstream scripts.

## How to interpret results

This tool is a **diagnostic aid**, not an indexing or ranking oracle.

For example:

- A `200` response means the HTTP request succeeded; it does not prove indexing.
- A canonical tag is an implementation signal; it does not prove that a search engine selected that URL as canonical.
- `noindex` in a page-level directive is a strong implementation signal, but the tool does not determine how a search engine will process every edge case.
- A redirect chain can be worth investigating, but the appropriate implementation depends on the site's architecture and intent.

See [docs/methodology.md](docs/methodology.md) for the evidence model and limitations.

## Related MarketLatch resources

For a broader technical SEO audit workflow, see the [MarketLatch Technical SEO Audit Checklist](https://github.com/nadeemalamseo/technical-seo-audit-checklist).

MarketLatch publishes practical SEO and AI-search resources at [marketlatch.com](https://marketlatch.com/).

These links are provided as contextual references, not as a claim that using this tool improves rankings.

## Project status

This repository is intentionally lightweight. It is designed to be readable, testable, and useful as a small URL-level diagnostic component rather than a full crawler.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).

## License

No open-source license has been granted in this repository. Unless a separate license is added, the repository contents remain under their default copyright terms.
