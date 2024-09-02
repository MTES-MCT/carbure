import factory
from django.contrib.auth import get_user_model

from core.models import CarbureStockTransformation, Entity

User = get_user_model()


class CarbureStockTransformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarbureStockTransformation

    source_stock = None
    dest_stock = None

    transformation_type = CarbureStockTransformation.ETH_ETBE
    volume_deducted_from_source = factory.Faker("random_int", min=5000, max=10000)
    volume_destination = factory.Faker("random_int", min=5000, max=10000)
    metadata = {"volume_denaturant": 1000, "volume_etbe_eligible": 1000}
    entity = factory.Iterator(Entity.objects.all())
    transformed_by = factory.Iterator(User.objects.all())
    transformation_dt = factory.Faker("date_time_this_year")
