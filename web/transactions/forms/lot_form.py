from django import forms

from core.carburetypes import CarbureUnit
from core.models import CarbureLot, Entity, Biocarburant, MatierePremiere, Depot, Pays
from producers.models import ProductionSite


class LotForm(forms.Form):
    # choices
    UNITS = ((CarbureUnit.LITER, "l"), (CarbureUnit.KILOGRAM, "kg"), (CarbureUnit.LHV, "pci"))
    LOTS = CarbureLot.objects.all()
    ENTITIES = Entity.objects.all()
    PRODUCERS = Entity.objects.filter(entity_type=Entity.PRODUCER)
    BIOFUELS = Biocarburant.objects.all()
    FEEDSTOCKS = MatierePremiere.objects.all()
    COUNTRIES = Pays.objects.all()
    PRODUCTION_SITES = ProductionSite.objects.all()
    DEPOTS = Depot.objects.all()

    # lot fields
    transport_document_type = forms.CharField(required=False)
    transport_document_reference = forms.CharField(required=False)

    quantity = forms.FloatField(min_value=0, required=False)
    volume = forms.FloatField(min_value=0, required=False)
    unit = forms.ChoiceField(choices=UNITS, required=False)

    biofuel_code = forms.ModelChoiceField(queryset=BIOFUELS, to_field_name="code", required=False)
    feedstock_code = forms.ModelChoiceField(queryset=FEEDSTOCKS, to_field_name="code", required=False)
    country_code = forms.ModelChoiceField(queryset=COUNTRIES, to_field_name="code_pays", required=False)

    free_field = forms.CharField(required=False)

    eec = forms.FloatField(required=False)
    el = forms.FloatField(required=False)
    ep = forms.FloatField(required=False)
    etd = forms.FloatField(required=False)
    eu = forms.FloatField(required=False)
    esca = forms.FloatField(required=False)
    eccs = forms.FloatField(required=False)
    eccr = forms.FloatField(required=False)
    eee = forms.FloatField(required=False)

    carbure_producer_id = forms.ModelChoiceField(queryset=PRODUCERS, required=False)
    unknown_producer = forms.CharField(required=False)

    # multiple choice field to handle duplicate production sites
    carbure_production_site = forms.ModelMultipleChoiceField(
        queryset=PRODUCTION_SITES, to_field_name="name", required=False
    )

    unknown_production_site = forms.CharField(required=False)
    production_site_certificate = forms.CharField(required=False)
    production_site_certificate_type = forms.CharField(required=False)
    production_country_code = forms.ModelChoiceField(queryset=COUNTRIES, to_field_name="code_pays", required=False)
    production_site_commissioning_date = forms.DateField(required=False)
    production_site_double_counting_certificate = forms.CharField(required=False)

    carbure_supplier_id = forms.ModelChoiceField(queryset=ENTITIES, required=False)
    unknown_supplier = forms.CharField(required=False)
    supplier_certificate = forms.CharField(required=False)
    supplier_certificate_type = forms.CharField(required=False)
    vendor_certificate = forms.CharField(required=False)
    vendor_certificate_type = forms.CharField(required=False)
    delivery_type = forms.CharField(required=False)
    delivery_date = forms.DateField(required=False)
    carbure_client_id = forms.ModelChoiceField(queryset=ENTITIES, required=False)
    unknown_client = forms.CharField(required=False)
    carbure_delivery_site_depot_id = forms.ModelMultipleChoiceField(
        queryset=DEPOTS, to_field_name="depot_id", required=False
    )
    unknown_delivery_site = forms.CharField(required=False)
    delivery_site_country_code = forms.ModelChoiceField(queryset=COUNTRIES, to_field_name="code_pays", required=False)

    # grab only the values that are defined on the form data
    # and transform them so they can be applied directly to a CarbureLot
    # extract quantity data to its own dict to apply specific modifications
    def get_lot_data(self, ignore_empty=False):
        form_data = self.cleaned_data

        lot_data = {}
        quantity_data = {}

        for field in form_data:
            # ignore fields that were not send as part of the request
            if field not in self.data:
                continue
            # if the option is enabled, skip empty fields
            if ignore_empty and form_data[field] in ("", None):
                continue

            lot_field = FORM_TO_LOT_FIELD.get(field, field)

            if field in ("quantity", "unit", "volume", "weight", "lhv_amount"):
                quantity_data[field] = form_data[field]
            elif field == "carbure_production_site":
                producer = form_data["carbure_producer_id"]
                if producer:
                    lot_data["carbure_production_site"] = form_data[field].filter(producer=producer).first()
            elif field == "carbure_delivery_site":
                lot_data["carbure_delivery_site"] = form_data[field].first()
            elif field in FORM_TO_LOT_FIELD:
                lot_data[lot_field] = form_data[field]
            else:
                lot_data[field] = form_data[field]

        return lot_data, quantity_data


# map form fields to CarbureLot model fields
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
