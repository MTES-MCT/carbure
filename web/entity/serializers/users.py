from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Pays, UserRights
from core.serializers import UserEntitySerializer as EntityUserEntitySerializer
from core.serializers import UserRightsRequestsSerializer as UserRightsRequestsSeriaizer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "email",
        ]


class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ["code_pays", "name", "name_en", "is_in_europe"]


class EntityMetricsSerializer(serializers.Serializer):
    entity = EntityUserEntitySerializer()
    users = serializers.IntegerField()
    requests = serializers.IntegerField()
    depots = serializers.IntegerField()
    production_sites = serializers.IntegerField()
    certificates = serializers.IntegerField()
    certificates_pending = serializers.IntegerField()
    double_counting = serializers.IntegerField()
    double_counting_requests = serializers.IntegerField()
    charge_points_accepted = serializers.IntegerField()
    charge_points_pending = serializers.IntegerField()
    meter_readings_accepted = serializers.IntegerField()
    meter_readings_pending = serializers.IntegerField()


class SimplifiedUserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserRightsSeriaizer(serializers.ModelSerializer):
    entity = EntityUserEntitySerializer()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = UserRights
        fields = ["name", "email", "entity", "role", "expiration_date"]

    @extend_schema_field(serializers.CharField)
    def get_name(self, obj):
        return obj.user.name

    @extend_schema_field(serializers.EmailField)
    def get_email(self, obj):
        return obj.user.email


class UserRightsResponseSeriaizer(serializers.Serializer):
    rights = UserRightsSeriaizer(many=True)
    requests = UserRightsRequestsSeriaizer(many=True)
