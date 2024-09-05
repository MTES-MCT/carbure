import os
import traceback

import sentry_sdk
from django.conf import settings

from core.carburetypes import CarbureError
from core.common import ErrorResponse


# general middleware that will catch any uncaught error in endpoints, and return a clean error response
class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if settings.DEBUG or os.getenv("TEST"):
            traceback.print_exc()
            return ErrorResponse(500, CarbureError.UNKNOWN_ERROR, message=str(exception))
        else:
            sentry_sdk.capture_exception(exception)
            return ErrorResponse(500, CarbureError.UNKNOWN_ERROR)
