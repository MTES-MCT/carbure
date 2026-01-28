import os
import traceback

from django.conf import settings
from sentry_sdk import capture_exception, logger


def should_log_to_sentry():
    return settings.WITH_SENTRY


def should_print_on_standard_output():
    return settings.DEBUG and not os.getenv("TEST")


def _log(log_level, message, additional_infos):
    additional_infos = additional_infos or {}

    if should_log_to_sentry():
        log_function = getattr(logger, log_level)
        log_function(message, attributes=additional_infos)

    if should_print_on_standard_output():
        print(f"[{log_level}] {message}")
        if additional_infos:
            print(f"Additional information: {additional_infos}")


def log_error(message, additional_infos=None):
    _log("error", message, additional_infos)


def log_exception(e):
    if should_log_to_sentry():
        capture_exception(e)

    if should_print_on_standard_output():
        traceback.print_exception(e)


def log_warning(message, additional_infos=None):
    _log("warning", message, additional_infos)
