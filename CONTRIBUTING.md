# Contributing

Thanks for helping improve Technical SEO URL Checker.

## Before opening a change

1. Read the README and methodology.
2. Keep the tool focused on URL-level diagnostics.
3. Add or update tests for behavior changes.
4. Keep observations separate from claims about search-engine outcomes.
5. Avoid features that require bypassing authentication, WAF controls, rate limits, or other access restrictions.

## Development

Create an environment and install dependencies:

```bash
python -m venv .venv
```

Activate the environment using the normal command for your operating system, then run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Pull requests

Explain:

- what changed
- why the change is useful
- how it was tested
- any new limitations or compatibility considerations

Please avoid marketing claims, ranking guarantees, or changes whose primary purpose is adding promotional links.
