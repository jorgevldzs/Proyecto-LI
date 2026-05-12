from pathlib import Path

import yaml
from django.shortcuts import render
from django.utils import timezone

from pages.models import Event, MainPagePhoto

_CONTENT_FILE = Path(__file__).parent / "content.yaml"


def _load_content():
    try:
        with open(_CONTENT_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def home(request):
    content = _load_content()
    photos = MainPagePhoto.objects.filter(is_visible=True)
    events = Event.objects.filter(is_visible=True, event_date__gte=timezone.now()).order_by("event_date")[:5]
    return render(request, "pages/home.html", {
        "content": content,
        "photos": photos,
        "events": events,
    })
