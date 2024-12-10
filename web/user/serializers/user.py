from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Entity, ExternalAdminRights, UserRights, UserRightsRequests
from doublecount.serializers import CountrySerializer


class UserEntitySerializer(serializers.ModelSerializer):
    registered_country = CountrySerializer(required=False)
    ext_admin_pages = serializers.SerializerMethodField()

    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "is_enabled",
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
        ]
        read_only_fields = fields

    @extend_schema_field(
        serializers.ListField(child=serializers.ChoiceField(choices=[r[1] for r in ExternalAdminRights.RIGHTS]))
    )
    def get_ext_admin_pages(self, obj):
        if obj.entity_type == Entity.EXTERNAL_ADMIN:
            return [e.right for e in obj.externaladminrights_set.all()]
        return None


class UserRightsRequestsSerializer(serializers.ModelSerializer):
    entity = UserEntitySerializer()
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
        read_only_fields = ["role", "status"]

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_user(self, obj):
        return [obj.user.email]


class UserRightsSerializer(serializers.ModelSerializer):
    entity = UserEntitySerializer()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = UserRights
        fields = ["name", "email", "entity", "role", "expiration_date"]
        read_only_fields = ["role"]

    @extend_schema_field(serializers.CharField)
    def get_name(self, obj):
        return obj.user.name

    @extend_schema_field(serializers.EmailField)
    def get_email(self, obj):
        return obj.user.email


class UserSettingsResponseSeriaizer(serializers.Serializer):
    email = serializers.EmailField()
    rights = UserRightsSerializer(many=True)
    requests = UserRightsRequestsSerializer(many=True)


class ResponseSuccessSerializer(serializers.Serializer):
    status = serializers.CharField()
