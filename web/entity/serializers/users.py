from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Entity, Pays, UserRights, UserRightsRequests


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


class EntityUserEntitySerializer(serializers.ModelSerializer):
    registered_country = PaysSerializer()
    ext_admin_pages = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "entity_type",
            "has_mac",
            "has_trading",
            "has_direct_deliveries",
            "has_stocks",
            "legal_name",
            "registration_id",
            "sustainability_officer",
            "sustainability_officer_phone_number",
            "sustainability_officer_email",
            "registered_address",
            "registered_zipcode",
            "registered_city",
            "registered_country",
            "default_certificate",
            "preferred_unit",
            "has_saf",
            "has_elec",
            "activity_description",
            "website",
            "vat_number",
            "ext_admin_pages",
            "is_enabled",
        ]

    @extend_schema_field(serializers.ListField)
    def get_ext_admin_pages(self, obj):
        if obj.entity_type == Entity.EXTERNAL_ADMIN:
            return [e.right for e in obj.externaladminrights_set.all()]
        return None


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


class UserRightsRequestsSeriaizer(serializers.ModelSerializer):
    entity = EntityUserEntitySerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserRightsRequests
        fields = [
            "id",
            "user",
            "entity",
            "date_requested",
            "status",
            "comment",
            "role",
            "expiration_date",
        ]

    @extend_schema_field(
        {
            "type": "array",
            "items": {
                "type": "string",
            },
        }
    )
    def get_user(self, obj):
        return [obj.user.email]


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
