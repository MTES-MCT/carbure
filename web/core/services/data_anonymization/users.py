"""
Anonymiseur spécialisé pour les utilisateurs (User).
"""

from django.contrib.auth import get_user_model

from .base import Anonymizer
from .utils import anonymize_fields_and_collect_modifications

User = get_user_model()


class UserAnonymizer(Anonymizer):
    def get_model_name(self):
        return "Users"

    def get_queryset(self):
        return User.objects.all()

    def get_updated_fields(self):
        return ["email", "name"]

    def process(self, user):
        return anonymize_fields_and_collect_modifications(
            user,
            {
                "email": f"user{user.id}@anonymized.local",
                "name": f"Utilisateur {user.id}",
            },
        )
