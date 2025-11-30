# Project Overview — python-utilities

This document summarizes the `python-utilities` project, its key components, how it works, runtime requirements, and recommended next steps.

## High-level purpose
`python-utilities` is a small collection of utilities focused around parsing certificate information from text (output captured from cert tools) and notifying about upcoming expirations via email.

## Repository layout

```
python-utilities/
├── README.md
├── requirements.txt
├── input.txt                # sample input (cert listing) used by tools
├── OVERVIEW.md              # (this file)
├── src/
│   ├── main.py              # CLI entrypoint: parse file, filter expiring certs, send email
│   └── utils/
│       ├── helpers.py       # Certificate class, parse_certificates, HTML formatting helper
│       └── email_sender.py  # send_email() using Plunk API
└── build/                   # build artifacts (not usually edited)
```

## Key components

- `src/main.py`
  - CLI entrypoint. Accepts a `file_path` argument. Steps:
    1. Parse certificates using `parse_certificates(file_path)`
    2. Compute `threshold_date = now_utc + 10 days`
    3. Filter certificates where parsed `expiry_date` (timezone-aware) is <= threshold
    4. Print certificates expiring soon and, if any, prepare an HTML table and send an email
  - Reads `PLUNK_API_KEY` from environment to authenticate the email API. Raises if missing.

- `src/utils/helpers.py`
  - `Certificate` class: holds fields parsed from the input (name, serial_number, key_type, domains, expiry_date, certificate_path, private_key_path, status).
  - `parse_certificates(file_path)`: reads the provided file line-by-line and constructs `Certificate` objects. Expects lines like `Certificate Name:`, `Expiry Date:`, `Domains:`, etc.
  - `format_certificates_as_html_table(certificates)`: produces an HTML `<table>` string used as the email body.

- `src/utils/email_sender.py`
  - `send_email(api_key, recipient_email, subject, body)`: posts to Plunk API (`https://api.useplunk.com/v1/send`) with a JSON payload. The function raises for non-2xx responses.

- `input.txt`
  - Sample cert list produced by cert tooling. Useful for testing the parser. Contains entries with timezone-aware expiry timestamps (e.g. `2025-09-18 13:27:01+00:00`).

## Runtime / dependencies

- Python 3.8+ recommended.
- See `requirements.txt` (currently pins `requests==2.25.1`). Install via:

```bash
pip install -r requirements.txt
```

## Environment variables

- `PLUNK_API_KEY` — required by `src/main.py` when sending emails. Example:

```bash
export PLUNK_API_KEY="your_actual_api_key"
```

## How to run

From the repository root:

```bash
export PLUNK_API_KEY="your_actual_api_key"
.venv/bin/python src/main.py input.txt
```

Or if using system Python:

```bash
python src/main.py input.txt
```

The script will print any certificates expiring within the next 10 days (UTC). If any are found, it will send an email containing an HTML table of those certificates.

## Notes and assumptions

- The parser expects the input file to include `Expiry Date:` lines where the date string includes a timezone offset (e.g. `+00:00`). The main code uses `datetime.strptime(..., "%Y-%m-%d %H:%M:%S%z")` to parse those strings.
- `main.py` uses `datetime.now(timezone.utc)` to ensure comparisons are made between offset-aware datetimes.
- The `email_sender.send_email` function posts to Plunk; make sure the Plunk API contract (payload keys) matches the API your account expects. The current implementation sends `to`, `subject`, `body` keys — modify if Plunk requires `html` or other fields.

## Extension points / recommended improvements

1. Tests: add unit tests for `parse_certificates` (happy + edge cases: missing fields, multiple certs, malformed expiry dates).
2. Robust parsing: convert `expiry_date` strings to `datetime` objects inside the `Certificate` constructor for easier filtering and avoid repeated parse calls.
3. Config management: allow `PLUNK_API_KEY` and sender/recipient addresses to be provided via a config file (e.g. `config.yaml`) or CLI flags in addition to environment variables.
4. Email formatting: use a templating engine (Jinja2) to build more robust HTML emails and support both plain-text and HTML parts.
5. CI / linting: add a GitHub Actions workflow for tests and linting.

## Quick troubleshooting

- TypeError comparing naive/aware datetimes: ensure `datetime.now(timezone.utc)` is used (already the case in `main.py`).
- Missing `PLUNK_API_KEY`: `main.py` will raise `ValueError` — set the environment variable before running.

## Next steps completed in this session

- Read the main project files and created this `OVERVIEW.md` summarizing the repository.

---

If you want, I can also:
- Create simple unit tests for `parse_certificates`.
- Convert `expiry_date` fields to `datetime` objects in `helpers.py` (safer comparisons).
- Add a small GitHub Actions workflow to run tests on push.
