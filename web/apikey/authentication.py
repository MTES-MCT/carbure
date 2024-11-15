import functools

from django.db.models import F
from django.utils import timezone
from django_otp import user_has_device
from django_otp.middleware import is_verified
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apikey.models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Récupérer l'en-tête Authorization
        auth = request.headers.get("Authorization")
        if not auth:
            return None

        # Vérifie si le préfixe est correct (Api-Key)
        if not auth.startswith("Api-Key "):
            raise AuthenticationFailed("The Api-Key prefix is missing.")

        # Extraire la clé API
        key = auth.split(" ")[1]

        # Récupérer l'utilisateur associé
        apikey = APIKey.objects.filter(key=key, revoked=False).first()
        if not apikey:
            raise AuthenticationFailed("Your api key is invalid or has been revoked.")

        user = apikey.user

        # verification OTP
        if not user_has_device(user):
            raise AuthenticationFailed("User not OTP verified.")

        device = EmailDevice.objects.get(user=user)
        user.otp_device = device
        user.is_verified = functools.partial(is_verified, user)

        # mise a jour de l'api key
        apikey.last_used = timezone.now()
        apikey.usage_count = F("usage_count") + 1
        apikey.save(update_fields=["last_used", "usage_count"])

        return (user, None)
