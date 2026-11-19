from csp.middleware import CSPMiddleware
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase


class ContentSecurityPolicyTest(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CSPMiddleware(lambda request: HttpResponse())

    def test_public_responses_keep_security_policy(self):
        response = self.middleware(self.factory.get("/"))
        directives = {
            parts[0]: set(parts[1:])
            for directive in response["Content-Security-Policy"].split(";")
            if (parts := directive.split())
        }

        self.assertEqual(
            directives["default-src"],
            {
                "'self'",
                "stats.beta.gouv.fr",
                "metabase.carbure.beta.gouv.fr",
                "www.data.gouv.fr",
                "https://*.tile.openstreetmap.org/",
                "sentry.incubateur.net",
                "https://tally.so",
                "contact.carbure.beta.gouv.fr",
            },
        )
        self.assertEqual(directives["frame-src"], directives["default-src"])
        self.assertEqual(directives["img-src"], directives["default-src"] | {"data:"})
        self.assertEqual(directives["style-src"], {"'self'"})
        self.assertEqual(
            directives["script-src"],
            directives["default-src"]
            | {
                "'sha256-xVQ4mcypV0CvOtZpQgVcKpcoNvdUkR9BrwZBrtBbU+w='",
                "'sha256-l0hQskZAA39ZNB1SAbclU+zKPtFeMvhhkjKEgiL2HI0='",
                "'sha256-/kXZODfqoc2myS1eI6wr0HH8lUt+vRhW8H/oL+YJcMg='",
            },
        )

    def test_admin_responses_are_exempt(self):
        response = self.middleware(self.factory.get("/admin/login/"))

        self.assertNotIn("Content-Security-Policy", response)

    def test_admin_api_responses_are_protected(self):
        response = self.middleware(self.factory.get("/api/transactions/admin/map/"))

        self.assertIn("Content-Security-Policy", response)
