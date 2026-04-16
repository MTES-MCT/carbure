from django.conf import settings
from django.db import models


class UserPreferences(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_entity = models.ForeignKey("core.Entity", blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = "users_preferences"
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"


class UserRights(models.Model):
    RO = "RO"
    RW = "RW"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    ROLES = ((RO, "Lecture Seule"), (RW, "Lecture/Écriture"), (ADMIN, "Administrateur"), (AUDITOR, "Auditeur"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=32, choices=ROLES, default=RO)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.user.email, self.entity.name)

    def natural_key(self):
        return {
            "name": self.user.name,
            "email": self.user.email,
            "entity": self.entity.natural_key(),
            "role": self.role,
            "expiration_date": self.expiration_date,
        }

    class Meta:
        db_table = "users_rights"
        verbose_name = "User Right"
        verbose_name_plural = "Users Rights"
        unique_together = [("user", "entity")]


class UserRightsRequests(models.Model):
    STATUS_TYPES = (
        ("PENDING", "En attente de validation"),
        ("ACCEPTED", "Accepté"),
        ("REJECTED", "Refusé"),
        ("REVOKED", "Révoqué"),
    )

    RO = "RO"
    RW = "RW"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    ROLES = ((RO, "Lecture Seule"), (RW, "Lecture/Écriture"), (ADMIN, "Administrateur"), (AUDITOR, "Auditeur"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey("core.Entity", on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_TYPES, default="PENDING")
    comment = models.TextField(blank=True, null=True)

    role = models.CharField(max_length=32, choices=ROLES, default=RO)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def natural_key(self):
        return {
            "id": self.id,
            "user": self.user.natural_key(),
            "entity": self.entity.natural_key(),
            "date_requested": self.date_requested,
            "status": self.status,
            "comment": self.comment,
            "role": self.role,
            "expiration_date": self.expiration_date,
        }

    class Meta:
        db_table = "users_rights_requests"
        verbose_name = "User Right Request"
        verbose_name_plural = "Users Rights Requests"
