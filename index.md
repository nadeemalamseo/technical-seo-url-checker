# Technical SEO URL Checker

Technical SEO URL Checker is a small Python utility for inspecting URL-level HTTP and HTML signals.

## Quick start

```bash
python -m pip install -r requirements.txt
python seo_url_checker.py https://example.com/
```

For structured output:

```bash
python seo_url_checker.py https://example.com/ --json
```

See the [README](README.md) for the complete usage guide and [methodology](docs/methodology.md) for interpretation and limitations.

## Scope

The project focuses on observable evidence such as HTTP status, redirects, canonical implementation, robots directives, title, and meta description. It does not determine search-engine indexing or ranking outcomes.
