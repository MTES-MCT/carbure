from sentry_sdk import capture_exception, logger


def log_error(error_message, additional_infos=None):
    if additional_infos is None:
        additional_infos = {}
    logger.error(error_message, attributes=additional_infos)


def log_exception(e):
    capture_exception(e)


def log_warning(message, additional_infos=None):
    additional_infos = additional_infos or {}
    logger.warning(message, attributes=additional_infos)
