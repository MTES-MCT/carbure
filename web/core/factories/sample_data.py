from django.contrib.auth import get_user_model

from core.models import Entity, ExternalAdminRights, Pays, UserRights

User = get_user_model()


ADMIN_EMAIL = "admin@carbure.local"
USER_EMAIL = "user@carbure.local"


def setup_admin_user() -> User:
    admin = User.objects.filter(email=ADMIN_EMAIL).first()
    if admin is None:
        admin = User.objects.create_superuser(
            email=ADMIN_EMAIL,
            name="Carbure Admin",
            password="password",
        )

    return admin


def setup_regular_user() -> User:
    user = User.objects.filter(email=USER_EMAIL).first()
    if user is None:
        user = User.objects.create_user(
            email=USER_EMAIL,
            name="Carbure User",
            password="password",
        )

    return user


def setup_france() -> Pays:
    france, _ = Pays.objects.get_or_create(
        code_pays="FR",
        defaults={
            "name": "France",
            "name_en": "France",
            "is_in_europe": True,
        },
    )

    return france


def set_user_access(user: User, entity: Entity, role: str):
    UserRights.objects.update_or_create(
        user=user,
        entity=entity,
        defaults={"role": role},
    )


def setup_external_admin_entity(name: str, external_entity_type: str) -> Entity:
    entity, _ = Entity.objects.get_or_create(
        name=name,
        entity_type=Entity.EXTERNAL_ADMIN,
    )

    ExternalAdminRights.objects.get_or_create(
        entity=entity,
        right=external_entity_type,
    )

    return entity


def create_sample_data():
    setup_admin_user()
    setup_regular_user()
    setup_france()
