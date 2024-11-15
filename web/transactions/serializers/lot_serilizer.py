from rest_framework import serializers

from core.carburetypes import CarbureUnit
from core.models import Biocarburant, Entity, MatierePremiere, Pays
from transactions.models import Depot, ProductionSite

FORM_TO_LOT_FIELD = {
    "biofuel_code": "biofuel",
    "feedstock_code": "feedstock",
    "country_code": "country_of_origin",
    "carbure_producer_id": "carbure_producer",
    "production_country_code": "production_country",
    "carbure_supplier_id": "carbure_supplier",
    "carbure_client_id": "carbure_client",
    "carbure_delivery_site_depot_id": "carbure_delivery_site",
    "delivery_site_country_code": "delivery_site_country",
}


class LotSerializer(serializers.Serializer):
    # choices for units
    UNITS = (
        (CarbureUnit.LITER, "l"),
        (CarbureUnit.KILOGRAM, "kg"),
        (CarbureUnit.LHV, "pci"),
    )

    # lot fields
    transport_document_type = serializers.CharField(required=False)
    transport_document_reference = serializers.CharField(required=False)

    quantity = serializers.FloatField(min_value=0, required=False)
    volume = serializers.FloatField(min_value=0, required=False)
    unit = serializers.ChoiceField(choices=UNITS, required=False)

    biofuel_code = serializers.SlugRelatedField(slug_field="code", queryset=Biocarburant.objects.all(), required=False)
    feedstock_code = serializers.SlugRelatedField(slug_field="code", queryset=MatierePremiere.objects.all(), required=False)
    country_code = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all(), required=False)

    free_field = serializers.CharField(required=False)

    # Emissions fields
    eec = serializers.FloatField(required=False)
    el = serializers.FloatField(required=False)
    ep = serializers.FloatField(required=False)
    etd = serializers.FloatField(required=False)
    eu = serializers.FloatField(required=False)
    esca = serializers.FloatField(required=False)
    eccs = serializers.FloatField(required=False)
    eccr = serializers.FloatField(required=False)
    eee = serializers.FloatField(required=False)

    carbure_producer_id = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(entity_type=Entity.PRODUCER), required=False
    )
    unknown_producer = serializers.CharField(required=False)

    carbure_production_site = serializers.SlugRelatedField(
        slug_field="name",
        queryset=ProductionSite.objects.all(),
        required=False,
        many=True,
    )
    unknown_production_site = serializers.CharField(required=False)
    production_site_certificate = serializers.CharField(required=False)
    production_site_certificate_type = serializers.CharField(required=False)
    production_country_code = serializers.SlugRelatedField(
        slug_field="code_pays", queryset=Pays.objects.all(), required=False
    )
    production_site_commissioning_date = serializers.DateField(required=False)
    production_site_double_counting_certificate = serializers.CharField(required=False)

    carbure_supplier_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    unknown_supplier = serializers.CharField(required=False)
    supplier_certificate = serializers.CharField(required=False)
    supplier_certificate_type = serializers.CharField(required=False)
    vendor_certificate = serializers.CharField(required=False)
    vendor_certificate_type = serializers.CharField(required=False)
    delivery_type = serializers.CharField(required=False)
    delivery_date = serializers.DateField(required=False)
    carbure_client_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=False)
    unknown_client = serializers.CharField(required=False)
    carbure_delivery_site_depot_id = serializers.SlugRelatedField(
        slug_field="customs_id", queryset=Depot.objects.all(), required=False, many=True
    )
    unknown_delivery_site = serializers.CharField(required=False)
    delivery_site_country_code = serializers.SlugRelatedField(
        slug_field="code_pays", queryset=Pays.objects.all(), required=False
    )

    def validate_carbure_production_site(self, value):
        """
        Retourner un QuerySet vide si la liste est vide ou non fournie.
        """
        if not value:
            return ProductionSite.objects.none()

        production_sites = ProductionSite.objects.filter(name__in=[obj.name for obj in value])
        if len(production_sites) != len(value):
            raise serializers.ValidationError("Un ou plusieurs noms de sites de production sont invalides.")

        return production_sites

    def validate_carbure_delivery_site_depot_id(self, value):
        """
        Retourner un QuerySet vide si la liste est vide ou non fournie.
        """
        if not value:
            return Depot.objects.none()

        carbure_delivery_site_depot = Depot.objects.filter(customs_id__in=[obj.depot_id for obj in value])
        if len(carbure_delivery_site_depot) != len(value):
            raise serializers.ValidationError("Un ou plusieurs carbure_delivery_site_depot sont invalides.")

        return carbure_delivery_site_depot

    def get_lot_data(self, validated_data, data, ignore_empty=False):
        lot_data = {}
        quantity_data = {}

        for field, value in validated_data.items():
            if field not in data:
                continue
            if ignore_empty and value in ("", None):
                continue

            lot_field = FORM_TO_LOT_FIELD.get(field, field)

            if field in ("quantity", "unit", "volume", "weight", "lhv_amount"):
                quantity_data[field] = value
            elif field == "carbure_production_site":
                producer = validated_data.get("carbure_producer_id")
                if producer:
                    lot_data["carbure_production_site"] = value.filter(producer=producer).first()
            elif field == "carbure_delivery_site_depot_id":
                lot_data["carbure_delivery_site"] = value.first()
            elif field in FORM_TO_LOT_FIELD:
                lot_data[lot_field] = value
            else:
                lot_data[field] = value

        return lot_data, quantity_data
