from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF, used on local only."""

    def enforce_csrf(self, request):
        return
