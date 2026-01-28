import os

from django.conf import settings

from adapters.logger import log_exception
from core.carburetypes import CarbureError
from core.common import ErrorResponse


# general middleware that will catch any uncaught error in endpoints, and return a clean error response
class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, _, exception):
        log_exception(exception)

        if settings.DEBUG or os.getenv("TEST"):
            return ErrorResponse(500, CarbureError.UNKNOWN_ERROR, message=str(exception))
        else:
            return ErrorResponse(500, CarbureError.UNKNOWN_ERROR)
