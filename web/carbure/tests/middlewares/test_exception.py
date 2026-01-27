from unittest import TestCase
from unittest.mock import patch

from carbure.middlewares.exception import ExceptionMiddleware


class ExceptionMiddlewareTest(TestCase):
    def setUp(self):
        self.patched_log_exception = patch("carbure.middlewares.exception.log_exception").start()

    def tearDown(self):
        patch.stopall()

    def test_logs_exceptions(self):
        middleware = ExceptionMiddleware(lambda: "")
        self.patched_log_exception.assert_not_called()

        with patch.dict("os.environ") as patched_environment:
            patched_environment["IMAGE_TAG"] = "prod"
            del patched_environment["TEST"]

            exception = Exception("oops")
            middleware.process_exception(None, exception)

        self.patched_log_exception.assert_called_with(exception)
