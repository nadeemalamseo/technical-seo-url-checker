# Technical SEO URL Checker

Technical SEO URL Checker is a small Python utility for inspecting URL-level HTTP and HTML signals.

## Get the tool

This is a **command-line tool**, not a browser-based checker.

[Download the latest source as a ZIP](https://github.com/nadeemalamseo/technical-seo-url-checker/archive/refs/heads/main.zip) or open the [GitHub repository](https://github.com/nadeemalamseo/technical-seo-url-checker).

After downloading and extracting:

```bash
python -m pip install -r requirements.txt
python seo_url_checker.py https://example.com/
python seo_url_checker.py https://example.com/ --json
```

For structured output:

```bash
python seo_url_checker.py https://example.com/ --json
```

See the [README](README.md) for the complete usage guide and [methodology](docs/methodology.md) for interpretation and limitations.

## Scope

The project focuses on observable evidence such as HTTP status, redirects, canonical implementation, robots directives, title, and meta description. It does not determine search-engine indexing or ranking outcomes.

## Related resource

For additional context on indexing states and how to investigate a URL that has been crawled but is not currently indexed, see [Crawled – Currently Not Indexed: What Google Means and How to Fix It](https://marketlatch.com/crawled-currently-not-indexed/).
