from django.contrib.auth import get_user_model

from core.models import Entity, UserRights

User = get_user_model()

ADMIN_EMAIL = "admin@carbure.local"
USER_EMAIL = "user@carbure.local"


def setup_users():
    admin = User.objects.filter(email=ADMIN_EMAIL).first()
    if admin is None:
        admin = User.objects.create_superuser(
            email=ADMIN_EMAIL,
            name="Carbure Admin",
            password="password",
        )

    user = User.objects.filter(email=USER_EMAIL).first()
    if user is None:
        user = User.objects.create_user(
            email=USER_EMAIL,
            name="Carbure User",
            password="password",
        )


def get_admin_user() -> User:
    return User.objects.get(email=ADMIN_EMAIL)


def get_regular_user() -> User:
    return User.objects.get(email=USER_EMAIL)


def set_user_access(user: User, entity: Entity, role: str):
    UserRights.objects.update_or_create(
        user=user,
        entity=entity,
        defaults={"role": role},
    )
