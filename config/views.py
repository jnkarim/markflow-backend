"""Small project-level endpoints."""

from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    """Return a simple response used by hosting health checks."""
    return JsonResponse({"status": "ok", "service": "markflow-backend"})
