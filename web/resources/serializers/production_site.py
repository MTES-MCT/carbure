from rest_framework import serializers

from producers.models import (
    Entity,
    ProductionSite,
    ProductionSiteInput,
    ProductionSiteOutput,
)

from .country import PaysSerializer


class ProductionSiteInputSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    is_double_compte = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ProductionSiteInput
        fields = ["code", "name", "is_double_compte", "category"]

    def get_code(self, obj):
        return obj.matiere_premiere.code

    def get_name(self, obj):
        return obj.matiere_premiere.name

    def get_is_double_compte(self, obj):
        return obj.matiere_premiere.is_double_compte

    def get_category(self, obj):
        return obj.matiere_premiere.category


class ProductionSiteOutputSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()

    class Meta:
        model = ProductionSiteOutput
        fields = ["name", "code"]

    def get_code(self, obj):
        return obj.biocarburant.code

    def get_name(self, obj):
        return obj.biocarburant.name


class ProducerSerializer(serializers.ModelSerializer):
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
        ]

    def get_ext_admin_pages(self, obj):
        if obj.entity_type == Entity.EXTERNAL_ADMIN:
            return [e.right for e in obj.externaladminrights_set.all()]
        return None


class ProductionSiteResourceSerializer(serializers.ModelSerializer):
    country = PaysSerializer()
    producer = ProducerSerializer()
    inputs = ProductionSiteInputSerializer(source="productionsiteinput_set", many=True, read_only=True)
    outputs = ProductionSiteOutputSerializer(source="productionsiteoutput_set", many=True, read_only=True)

    class Meta:
        model = ProductionSite
        fields = [
            "id",
            "name",
            "country",
            "date_mise_en_service",
            "ges_option",
            "eligible_dc",
            "dc_reference",
            "inputs",
            "outputs",
            "producer",
        ]
