import logging
import re

from django.conf import settings
from django.urls import Resolver404, resolve

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_HTTP_4XX_LOG_LEVEL = logging.ERROR
DEFAULT_MAX_BODY_LENGTH = 50000  # log no more than 3k bytes of content
SETTING_NAMES = {
    "log_level": "REQUEST_LOGGING_DATA_LOG_LEVEL",
    "http_4xx_log_level": "REQUEST_LOGGING_HTTP_4XX_LOG_LEVEL",
    "max_body_length": "REQUEST_LOGGING_MAX_BODY_LENGTH",
}
BINARY_REGEX = re.compile(r"(.+Content-Type:.*?)(\S+)/(\S+)(?:\r\n)*(.+)", re.S | re.I)
BINARY_TYPES = ("image", "application")
NO_LOGGING_ATTR = "no_logging"
NO_LOGGING_MSG_ATTR = "no_logging_msg"
NO_LOGGING_MSG = "No logging for this endpoint"
request_logger = logging.getLogger("django.request")


class Logger:
    def log(self, level, msg, logging_context):
        args = logging_context["args"]
        kwargs = logging_context["kwargs"]
        for line in re.split(r"\r?\n", str(msg)):
            request_logger.log(level, line, *args, **kwargs)

    def log_error(self, level, msg, logging_context):
        self.log(level, msg, logging_context)


class LoggingMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

        self.log_level = getattr(settings, SETTING_NAMES["log_level"], DEFAULT_LOG_LEVEL)
        self.http_4xx_log_level = getattr(settings, SETTING_NAMES["http_4xx_log_level"], DEFAULT_HTTP_4XX_LOG_LEVEL)
        for log_attr in ("log_level", "http_4xx_log_level"):
            level = getattr(self, log_attr)
            if level not in [
                logging.NOTSET,
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL,
            ]:
                raise ValueError("Unknown log level({}) in setting({})".format(level, SETTING_NAMES[log_attr]))

        self.max_body_length = getattr(settings, SETTING_NAMES["max_body_length"], DEFAULT_MAX_BODY_LENGTH)
        if not isinstance(self.max_body_length, int):
            raise ValueError(
                "{} should be int. {} is not int.".format(SETTING_NAMES["max_body_length"], self.max_body_length)
            )

        self.logger = Logger()
        self.boundary = ""
        self.cached_request_body = None

    def __call__(self, request):
        self.cached_request_body = request.body
        response = self.get_response(request)
        self.process_request(request, response)
        self.process_response(request, response)
        return response

    def process_request(self, request, response=None):
        skip_logging, because = self._should_log_route(request)
        if skip_logging:
            if because is not None:
                return self._skip_logging_request(request, because)
        else:
            return self._log_request(request, response)

    def _should_log_route(self, request):
        # request.urlconf may be set by middleware or application level code.
        # Use this urlconf if present or default to None.
        # https://docs.djangoproject.com/en/2.1/topics/http/urls/#how-django-processes-a-request
        # https://docs.djangoproject.com/en/2.1/ref/request-response/#attributes-set-by-middleware
        urlconf = getattr(request, "urlconf", None)

        try:
            route_match = resolve(request.path, urlconf=urlconf)
        except Resolver404:
            return False, None

        method = request.method.lower()
        view = route_match.func
        func = view
        # This is for "django rest framework"
        if hasattr(view, "cls"):
            if hasattr(view, "actions"):
                actions = view.actions
                method_name = actions.get(method)
                if method_name:
                    func = getattr(view.cls, view.actions[method], None)
            else:
                func = getattr(view.cls, method, None)
        elif hasattr(view, "view_class"):
            # This is for django class-based views
            func = getattr(view.view_class, method, None)
        no_logging = getattr(func, NO_LOGGING_ATTR, False)
        no_logging_msg = getattr(func, NO_LOGGING_MSG_ATTR, None)
        return no_logging, no_logging_msg

    def _skip_logging_request(self, request, reason):
        method_path = "{} {}".format(request.method, request.get_full_path())
        no_log_context = {
            "args": (),
            "kwargs": {"extra": {"no_logging": reason}},
        }
        self.logger.log(logging.INFO, method_path + " (not logged because '" + reason + "')", no_log_context)

    def _log_request(self, request, response):
        method_path = "{} {}".format(request.method, request.get_full_path())
        logging_context = self._get_logging_context(request, None)

        # Determine log level depending on response status
        log_level = self.log_level
        if response is not None:
            if response.status_code in range(400, 500):
                log_level = self.http_4xx_log_level
            elif response.status_code in range(500, 600):
                log_level = logging.ERROR

        self.logger.log(logging.INFO, method_path, logging_context)
        self._log_request_body(request, logging_context, log_level)

    def _log_request_body(self, request, logging_context, log_level):
        if self.cached_request_body is not None:
            content_type = request.META.get("CONTENT_TYPE", "")
            is_multipart = content_type.startswith("multipart/form-data")
            if is_multipart:
                self.boundary = "--" + content_type[30:]  # First 30 characters are "multipart/form-data; boundary="
            if is_multipart:
                self._log_multipart(self._chunked_to_max(self.cached_request_body), logging_context, log_level)
            else:
                self.logger.log(log_level, self._chunked_to_max(self.cached_request_body), logging_context)

    def process_response(self, request, response):
        resp_log = "{} {} - {}".format(request.method, request.get_full_path(), response.status_code)
        skip_logging, because = self._should_log_route(request)
        if skip_logging:
            if because is not None:
                self.logger.log_error(logging.INFO, resp_log, {"args": {}, "kwargs": {"extra": {"no_logging": because}}})
            return response
        logging_context = self._get_logging_context(request, response)

        if response.status_code in range(400, 500):
            if self.http_4xx_log_level == DEFAULT_HTTP_4XX_LOG_LEVEL:
                # default, log as per 5xx
                self.logger.log_error(logging.INFO, resp_log, logging_context)
                self._log_resp(logging.ERROR, response, logging_context)
            else:
                self.logger.log(self.http_4xx_log_level, resp_log, logging_context)
                self._log_resp(self.log_level, response, logging_context)
        elif response.status_code in range(500, 600):
            self.logger.log_error(logging.INFO, resp_log, logging_context)
            self._log_resp(logging.ERROR, response, logging_context)
        else:
            self.logger.log(logging.INFO, resp_log, logging_context)
            self._log_resp(self.log_level, response, logging_context)

        return response

    def _get_logging_context(self, request, response):
        """
        Returns a map with args and kwargs to provide additional context to calls to logging.log().
        This allows the logging context to be created per process request/response call.
        """
        return {
            "args": (),
            "kwargs": {"extra": {"request": request, "response": response}},
        }

    def _log_multipart(self, body, logging_context, log_level):
        """
        Splits multipart body into parts separated by "boundary", then matches each part to BINARY_REGEX
        which searches for existence of "Content-Type" and capture of what type is this part.
        If it is an image or an application replace that content with "(binary data)" string.
        This function will log "(multipart/form)" if body can't be decoded by utf-8.
        """
        try:
            body_str = body.decode()
        except UnicodeDecodeError:
            self.logger.log(log_level, "(multipart/form)", logging_context)
            return

        parts = body_str.split(self.boundary)
        last = len(parts) - 1
        for i, part in enumerate(parts):
            if "Content-Type:" in part:
                match = BINARY_REGEX.search(part)
                if match and match.group(2) in BINARY_TYPES and match.group(4) not in ("", "\r\n"):
                    part = match.expand(r"\1\2/\3\r\n\r\n(binary data)\r\n")

            if i != last:
                part = part + self.boundary

            # do not log anything containing a password
            if "password" in part:
                continue

            self.logger.log(log_level, part, logging_context)

    def _log_resp(self, level, response, logging_context):
        if re.match("^application/json", response.get("Content-Type", ""), re.I):
            # self.logger.log(level, response.headers, logging_context) - dont care about headers
            if response.streaming:
                # There's a chance that if it's streaming it's because large and it might hit
                # the max_body_length very often. Not to mention that StreamingHttpResponse
                # documentation advises to iterate only once on the content.
                # So the idea here is to just _not_ log it.
                self.logger.log(level, "(data_stream)", logging_context)
            else:
                self.logger.log(level, self._chunked_to_max(response.content), logging_context)

    def _chunked_to_max(self, msg):
        return msg[0 : self.max_body_length]
