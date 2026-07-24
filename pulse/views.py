from __future__ import annotations

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .services import FetchError, UrlValidationError, fetch_url, parse_html_metrics, validate_url


def home(request):
    return render(request, "pulse/index.html")


@require_GET
def audit_url(request):
    raw_url = (request.GET.get("url") or "").strip()
    if raw_url == "":
        return JsonResponse({"error": "Query parameter 'url' is required."}, status=400)

    try:
        validate_url(raw_url)
        fetched = fetch_url(raw_url)
    except UrlValidationError as error:
        return JsonResponse({"error": str(error)}, status=400)
    except FetchError as error:
        return JsonResponse({"error": str(error)}, status=error.status_code)

    content_type = (fetched.get("content_type") or "").lower()
    if "text/html" not in content_type:
        return JsonResponse(
            {
                "error": "URL responded with non-HTML content.",
                "http_status": fetched["status"],
                "response_time_ms": fetched["response_time_ms"],
                "content_type": fetched["content_type"],
            },
            status=415,
        )

    html = fetched["body"].decode("utf-8", errors="replace")
    metrics = parse_html_metrics(html)

    return JsonResponse(
        {
            "url": raw_url,
            "http_status": fetched["status"],
            "response_time_ms": fetched["response_time_ms"],
            "content_type": fetched["content_type"],
            **metrics,
        }
    )
