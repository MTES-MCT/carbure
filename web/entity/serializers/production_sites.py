from django.db import transaction
from django.db.models import Q
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from certificates.models import ProductionSiteCertificate
from core.models import Biocarburant, CarbureLot, EntityCertificate, GenericCertificate, MatierePremiere, Pays
from core.serializers import GenericCertificateSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.models import ProductionSite
from transactions.models.entity_site import EntitySite
from transactions.models.site import Site


class EntityProductionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()

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

    @extend_schema_field(FeedStockSerializer(many=True))
    def get_inputs(self, production_site):
        inputs = production_site.productionsiteinput_set.all()
        feedstocks = [input.matiere_premiere for input in inputs]
        return FeedStockSerializer(feedstocks, many=True).data

    @extend_schema_field(BiofuelSerializer(many=True))
    def get_outputs(self, production_site):
        outputs = production_site.productionsiteoutput_set.all()
        biofuels = [output.biocarburant for output in outputs]
        return BiofuelSerializer(biofuels, many=True).data

    @extend_schema_field(GenericCertificateSerializer(many=True))
    def get_certificates(self, production_site):
        prod_certificates = production_site.productionsitecertificate_set.all()
        certificates = [certificate.certificate.certificate for certificate in prod_certificates]
        return GenericCertificateSerializer(certificates, many=True).data


class EntityProductionSiteWriteSerializer(serializers.ModelSerializer):
    inputs = serializers.SlugRelatedField(
        many=True,
        slug_field="code",
        queryset=MatierePremiere.objects.all(),
        allow_empty=False,
    )

    outputs = serializers.SlugRelatedField(
        many=True,
        slug_field="code",
        queryset=Biocarburant.objects.all(),
        allow_empty=False,
    )

    certificates = serializers.SlugRelatedField(
        many=True,
        slug_field="certificate_id",
        queryset=GenericCertificate.objects.all(),
    )

    country_code = serializers.SlugRelatedField(
        source="country",
        slug_field="code_pays",
        queryset=Pays.objects.all(),
    )

    class Meta:
        model = ProductionSite
        fields = [
            "address",
            "certificates",
            "city",
            "country_code",
            "date_mise_en_service",
            "dc_reference",
            "eligible_dc",
            "ges_option",
            "inputs",
            "manager_email",
            "manager_name",
            "manager_phone",
            "name",
            "outputs",
            "postal_code",
            "site_siret",
        ]

    # use the Read serializer when consuming this serializer in a response
    def to_representation(self, instance):
        return EntityProductionSiteSerializer(instance).data

    @transaction.atomic
    def create(self, validated_data):
        entity_id = self.context.get("entity_id")

        feedstocks, biofuels, certificates = self.extract_relations(validated_data)

        production_site = Site.objects.create(
            **validated_data,
            site_type=Site.PRODUCTION_BIOLIQUID,
            created_by_id=entity_id,
        )

        EntitySite.objects.create(site=production_site, entity_id=entity_id)

        self.set_relations(production_site, feedstocks, biofuels, certificates)

        return production_site

    @transaction.atomic
    def update(self, production_site, validated_data):
        feedstocks, biofuels, certificates = self.extract_relations(validated_data)

        for attr, value in validated_data.items():
            setattr(production_site, attr, value)
        production_site.save()

        self.set_relations(production_site, feedstocks, biofuels, certificates)

        return production_site

    def extract_relations(self, validated_data):
        inputs = validated_data.pop("inputs", None)
        outputs = validated_data.pop("outputs", None)
        certificates = validated_data.pop("certificates", None)

        entity_id = self.context.get("entity_id")
        if certificates:
            entity_certificates = EntityCertificate.objects.filter(certificate__in=certificates, entity_id=entity_id)
        else:
            entity_certificates = None

        return inputs, outputs, entity_certificates

    def set_relations(self, production_site, feedstocks, biofuels, certificates):
        entity_id = self.context.get("entity_id")

        if feedstocks is not None:
            ProductionSiteInput.objects.filter(production_site=production_site).delete()
            inputs = [ProductionSiteInput(production_site=production_site, matiere_premiere=fs) for fs in feedstocks]
            ProductionSiteInput.objects.bulk_create(inputs)

        if biofuels is not None:
            ProductionSiteOutput.objects.filter(production_site=production_site).delete()
            outputs = [ProductionSiteOutput(production_site=production_site, biocarburant=bf) for bf in biofuels]
            ProductionSiteOutput.objects.bulk_create(outputs)

        if certificates is not None:
            ProductionSiteCertificate.objects.filter(production_site=production_site).delete()
            production_certificates = [
                ProductionSiteCertificate(production_site=production_site, certificate=ct, entity_id=entity_id)
                for ct in certificates
            ]
            ProductionSiteCertificate.objects.bulk_create(production_certificates)

        # Find related biofuel transactions and trigger background checks

        filter = Q()
        if biofuels is not None:
            filter |= Q(biofuel__in=biofuels)
        if feedstocks is not None:
            filter |= Q(feedstock__in=feedstocks)

        impacted_txs = CarbureLot.objects.filter(carbure_production_site=production_site).filter(filter)

        background_bulk_scoring(impacted_txs)
        background_bulk_sanity_checks(impacted_txs)
