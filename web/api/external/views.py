from rest_framework import routers, serializers, viewsets
from core.models import LotTransaction as Batch


# Serializers define the API representation.
class BatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Batch
        fields = ['dae', 'delivery_status']


# ViewSets define the view behavior.
class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'batches', BatchViewSet)
