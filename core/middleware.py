import logging

from django.db import DatabaseError

from .models import PageView


logger = logging.getLogger(__name__)


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if self.should_track(request, response):
            try:
                PageView.objects.create(
                    path=request.path[:260],
                    page_title=getattr(response, "reason_phrase", "")[:220],
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
                    referrer=request.META.get("HTTP_REFERER", "")[:200],
                )
            except DatabaseError:
                logger.exception("Unable to record page view for %s", request.path)
        return response

    def should_track(self, request, response):
        if request.method != "GET" or response.status_code >= 400:
            return False
        ignored_prefixes = ("/admin/", "/static/", "/media/", "/favicon.ico")
        return not request.path.startswith(ignored_prefixes)

    def get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
