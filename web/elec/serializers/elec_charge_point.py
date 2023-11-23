from rest_framework import serializers
from core.serializers import EntityPreviewSerializer
from elec.models import ElecChargePoint


class ElecChargePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecChargePoint
        fields = [
            "id",
            "cpo",
            # cpo excel data
            "charge_point_id",
            "current_type",
            "installation_date",
            "lne_certificate",
            "meter_reading_date",
            # "meter_reading_energy",
            "is_using_reference_meter",
            "is_auto_consumption",
            "has_article_4_regularization",
            "reference_meter_id",
            # transport.data.gouv.fr data
            "station_name",
            "station_id",
        ]

    cpo = EntityPreviewSerializer(read_only=True)
