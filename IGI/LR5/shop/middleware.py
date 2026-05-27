"""Middleware for resolving user timezone from browser cookie."""

from __future__ import annotations

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import unquote

from django.conf import settings
from django.utils import timezone


class BrowserTimezoneMiddleware:
    """Activate the timezone reported by the browser cookie if available."""

    cookie_name = "browser_tz"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw_tz_name = request.COOKIES.get(self.cookie_name) or request.session.get(self.cookie_name)
        tz_name = unquote(raw_tz_name) if raw_tz_name else None
        request.browser_timezone = None

        if tz_name:
            try:
                #timezone name
                timezone.activate(ZoneInfo(tz_name))
                request.browser_timezone = tz_name
            except ZoneInfoNotFoundError:
                timezone.deactivate()
            except Exception:
                timezone.deactivate()
        else:
            timezone.deactivate()

        request.active_timezone_name = request.browser_timezone or settings.TIME_ZONE
        response = self.get_response(request)
        return response
