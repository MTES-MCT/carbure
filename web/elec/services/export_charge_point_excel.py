import datetime

from core.excel import export_to_excel
from elec.serializers.elec_charge_point import ElecChargePointSerializer


def export_charge_points_to_excel(charge_points, entity):
    today = datetime.date.today()
    file = "/tmp/carbure_elec_charge_points_%s_%s.xlsx" % (entity.id, today.strftime("%Y%m%d_%H%M"))

    return export_to_excel(
        file,
        [
            {
                "label": "tickets",
                "rows": ElecChargePointSerializer(charge_points, many=True).data,
                "columns": [
                    {"label": "id", "value": "id"},
                    {"label": "cpo", "value": "cpo.name"},
                    # cpo excel data
                    {"label": "charge_point_id", "value": "charge_point_id"},
                    {"label": "current_type", "value": "current_type"},
                    {"label": "installation_date", "value": "installation_date"},
                    {"label": "lne_certificate", "value": "lne_certificate"},
                    {"label": "meter_reading_date", "value": "meter_reading_date"},
                    {"label": "meter_reading_energy", "value": "meter_reading_energy"},
                    {"label": "is_using_reference_meter", "value": "is_using_reference_meter"},
                    {"label": "is_auto_consumption", "value": "is_auto_consumption"},
                    {"label": "has_article_4_regularization", "value": "has_article_4_regularization"},
                    {"label": "reference_meter_id", "value": "reference_meter_id"},
                    # transport.data.gouv.fr data
                    {"label": "station_name", "value": "station_name"},
                    {"label": "station_id", "value": "station_id"},
                ],
            }
        ],
    )
