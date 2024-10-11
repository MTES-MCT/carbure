import secrets

from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.

usermodel = get_user_model()


class APIKey(models.Model):
    name = models.CharField(max_length=255, null=True)
    key = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(usermodel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.revoked
