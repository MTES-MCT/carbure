from rest_framework import serializers

from core.models import CarbureLot
from core.serializers import CarbureLotAdminSerializer, CarbureLotCSVSerializer, CarbureLotPublicSerializer
from transactions.models import Site as Depot


# mixin serializer to add specific GHG info for power and heat production
class CarbureLotPowerOrHeatSerializer(serializers.ModelSerializer):
    emission_electricity = serializers.SerializerMethodField()
    total_reduction_electricity = serializers.SerializerMethodField()
    emission_heat = serializers.SerializerMethodField()
    total_reduction_heat = serializers.SerializerMethodField()

    def get_emission_electricity(self, obj):
        if obj.carbure_delivery_site is None:
            return None

        plant, E_total, R_elec, C_elec, R_chaleur, C_chaleur = self.get_emission_operands(obj)

        E_elec = None
        if plant.depot_type == Depot.COGENERATION_PLANT:
            E_elec = (E_total / R_elec) * ((C_elec * R_elec) / (C_elec * R_elec + C_chaleur * R_chaleur))
        elif plant.depot_type == Depot.POWER_PLANT:
            E_elec = E_total / R_elec

        return round(E_elec, 2) if E_elec else None

    def get_total_reduction_electricity(self, obj):
        Ref_elec = 183.0  # gCO2/MJ
        E_elec = self.get_emission_electricity(obj)

        if E_elec is None:
            return None

        return round(100 * (Ref_elec - E_elec) / Ref_elec, 2)

    def get_emission_heat(self, obj):
        if obj.carbure_delivery_site is None:
            return None

        plant, E_total, R_elec, C_elec, R_chaleur, C_chaleur = self.get_emission_operands(obj)

        E_chaleur = None
        if plant.depot_type == Depot.COGENERATION_PLANT:
            E_chaleur = (E_total / R_chaleur) * ((C_chaleur * R_chaleur) / (C_elec * R_elec + C_chaleur * R_chaleur))
        if plant.depot_type == Depot.HEAT_PLANT:
            E_chaleur = E_total / R_chaleur

        return round(E_chaleur, 2) if E_chaleur else None

    def get_total_reduction_heat(self, obj):
        Ref_chaleur = 80.0  # gCO2/MJ
        E_chaleur = self.get_emission_heat(obj)

        if E_chaleur is None:
            return None

        return round(100 * (Ref_chaleur - E_chaleur) / Ref_chaleur, 2)

    def get_emission_operands(self, obj):
        plant = obj.carbure_delivery_site
        E_total = obj.ghg_total  # Total des émissions du lot en amont

        R_elec = plant.electrical_efficiency or 0  # Rendement électrique
        C_elec = 1  # Fraction de l'exergie dans l'électricité (100%)

        R_chaleur = plant.thermal_efficiency or 0  # Rendement thermique
        C_chaleur = (
            plant.useful_temperature / (plant.useful_temperature + 273.15) if plant.useful_temperature else 0
        )  # Fraction de l'exergie dans la chaleur utile

        return plant, E_total, R_elec, C_elec, R_chaleur, C_chaleur

    class Meta:
        model = CarbureLot
        fields = [
            "emission_electricity",
            "total_reduction_electricity",
            "emission_heat",
            "total_reduction_heat",
        ]


class CarbureLotPowerOrHeatProducerPublicSerializer(CarbureLotPublicSerializer, CarbureLotPowerOrHeatSerializer):
    class Meta(CarbureLotPublicSerializer.Meta, CarbureLotPowerOrHeatSerializer.Meta):
        fields = CarbureLotPublicSerializer.Meta.fields + CarbureLotPowerOrHeatSerializer.Meta.fields


class CarbureLotPowerOrHeatProducerAdminSerializer(CarbureLotAdminSerializer, CarbureLotPowerOrHeatSerializer):
    class Meta(CarbureLotAdminSerializer.Meta, CarbureLotPowerOrHeatSerializer.Meta):
        fields = CarbureLotAdminSerializer.Meta.fields + CarbureLotPowerOrHeatSerializer.Meta.fields


class CarbureLotPowerOrHeatProducerCSVSerializer(CarbureLotCSVSerializer, CarbureLotPowerOrHeatSerializer):
    class Meta(CarbureLotCSVSerializer.Meta, CarbureLotPowerOrHeatSerializer.Meta):
        fields = CarbureLotCSVSerializer.Meta.fields + CarbureLotPowerOrHeatSerializer.Meta.fields
