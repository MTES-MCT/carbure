from drf_spectacular.authentication import SessionScheme
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF, used on local only."""

    def enforce_csrf(self, request):
        return


# Spectacular maps cookieAuth only onto SessionAuthentication itself.
# This is the only subclass, so include it in that same scheme.
SessionScheme.match_subclasses = True
