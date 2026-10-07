from uuid import uuid4

import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from core.models import StoredFile
from entity.factories.entity import EntityFactory

User = get_user_model()


class StoredFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StoredFile

    name = "document.pdf"
    url = factory.LazyFunction(lambda: ContentFile(b"file content", name="document.pdf"))
    entity = factory.SubFactory(EntityFactory)
    user = factory.LazyFunction(
        lambda: User.objects.create_user(
            email=f"file-user-{uuid4().hex[:8]}@carbure.local",
            name="File User",
            password="password",
        )
    )
