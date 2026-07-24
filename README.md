# Page Pulse

Page Pulse is a Django web tool that audits any URL and returns quick page-quality metrics.

## Features

- Backend API endpoint: validates URL, fetches page, and returns JSON report
- Frontend UI: simple input + one-click audit + clean report table
- Failure handling for invalid URLs, timeouts, fetch failures, and non-HTML responses
- Unit tests for parsing logic (happy path + two failure cases)

## Tech Stack

- Python
- Django
- Standard library HTML parsing (`html.parser`) and HTTP fetching (`urllib`)

## Local Setup

1. Create and activate a virtual environment.
2. Install Django:
   ```bash
   pip install django
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the server:
   ```bash
   python manage.py runserver
   ```
5. Open:
   - UI: `http://127.0.0.1:8000/`
   - API: `http://127.0.0.1:8000/api/audit?url=https://example.com`

## API Contract

### Endpoint

`GET /api/audit?url=<absolute_http_or_https_url>`

### Success Response (200)

```json
{
  "url": "https://example.com",
  "http_status": 200,
  "response_time_ms": 148.22,
  "content_type": "text/html; charset=UTF-8",
  "page_title": "Example Domain",
  "meta_description": "Example description",
  "h1_count": 1,
  "images_missing_alt": 0,
  "approx_word_count": 42
}
```

### Error Responses

- `400` invalid or missing URL
  ```json
  { "error": "URL must include http:// or https:// and a valid host." }
  ```
- `504` timeout fetching upstream page
  ```json
  { "error": "Timed out while fetching URL." }
  ```
- `502` other upstream/network fetch errors
  ```json
  { "error": "Could not fetch URL." }
  ```
- `415` non-HTML response
  ```json
  {
    "error": "URL responded with non-HTML content.",
    "http_status": 200,
    "response_time_ms": 23.77,
    "content_type": "application/json"
  }
  ```

## Tests

Run:

```bash
python manage.py test pulse.tests
```

Included parser tests:

1. Happy path (title/meta/h1/images/word count extraction)
2. Failure case: non-string HTML input
3. Failure case: empty HTML input

## Design Decisions

1. **Use GET with query parameter for audit input**
   - Reasoning: the operation is read-only and easy to test directly from browser and curl without request-body setup.

2. **Use Python standard library for fetch/parsing**
   - Reasoning: keeps dependencies minimal and improves portability for quick setup in coding-assignment environments.

3. **Return explicit, typed HTTP error categories (400/415/502/504)**
   - Reasoning: separates client issues from upstream/network conditions so callers can handle retries and UX messaging correctly.

## Task Deliverable Notes

- **Public GitHub repo:** push this folder to a new GitHub repository.
- **Live deployed link:** deploy on a free tier (for example, Render/Railway/Fly.io).
- **Loom demo:** record a short walkthrough showing:
  - successful audit run
  - one failure path
  - one code area to improve with an extra day
