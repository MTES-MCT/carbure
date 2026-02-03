from sentry_sdk import logger


def log_error(error_message, additional_infos=None):
    if additional_infos is None:
        additional_infos = {}
    logger.error(error_message, attributes=additional_infos)
