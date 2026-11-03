from django.http import JsonResponse
from django.utils import timezone


def health_check(request):
    return JsonResponse({
        "status": "online",
        "service": "Atlas Finance API",
        "version": "1.0.0",
        "timestamp": timezone.now().isoformat(),
    })