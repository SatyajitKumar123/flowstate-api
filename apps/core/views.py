from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache


def health_check(request):
    """Basic health check endpoint."""
    return JsonResponse({"status": "healthy", "service": "flowstate-api"})


def readiness_check(request):
    """Readiness check - verifies dependencies are available."""
    checks = {
        "database": False,
    }

    # Check database
    try:
        connection.ensure_connection()
        checks["database"] = True
    except Exception:
        pass

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return JsonResponse(
        {"status": "ready" if all_healthy else "not_ready", "checks": checks},
        status=status_code,
    )