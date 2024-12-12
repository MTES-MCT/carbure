from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Biocarburant, MatierePremiere, Pays
from core.serializers import GenericCertificateSerializer
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.models import ProductionSite


class EntityFeedStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = ["name", "name_en", "code", "category", "is_double_compte"]


class EntityBiofuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biocarburant
        fields = ["name", "name_en", "code"]


class EntityCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ["name", "name_en", "code_pays", "is_in_europe"]


class EntityProductionSiteSerializer(serializers.ModelSerializer):
    country = EntityCountrySerializer(read_only=True)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    certificates = GenericCertificateSerializer(many=True)

    class Meta:
        model = ProductionSite
        fields = [
            "id",
            "address",
            "name",
            "country",
            "date_mise_en_service",
            "site_siret",
            "postal_code",
            "manager_name",
            "manager_phone",
            "manager_email",
            "ges_option",
            "eligible_dc",
            "dc_reference",
            "dc_number",
            "city",
            "certificates",
            "inputs",
            "outputs",
        ]

    @extend_schema_field(EntityFeedStockSerializer(many=True))
    def get_inputs(self, obj):
        inputs = ProductionSiteInput.objects.filter(production_site=obj)
        feedstocks = [input.matiere_premiere for input in inputs]
        return EntityFeedStockSerializer(feedstocks, many=True).data

    @extend_schema_field(EntityBiofuelSerializer(many=True))
    def get_outputs(self, obj):
        inputs = ProductionSiteOutput.objects.filter(production_site=obj)
        biofuels = [input.biocarburant for input in inputs]
        return EntityBiofuelSerializer(biofuels, many=True).data
