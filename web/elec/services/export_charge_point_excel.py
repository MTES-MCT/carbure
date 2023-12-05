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
                    {"label": "cpo", "value": "cpo"},
                    # cpo excel data
                    {"label": "charge_point_id", "value": "charge_point_id"},
                    {"label": "current_type", "value": "current_type"},
                    {"label": "installation_date", "value": "installation_date"},
                    {"label": "mid_id", "value": "mid_id"},
                    {"label": "measure_date", "value": "measure_date"},
                    {"label": "measure_energy", "value": "measure_energy"},
                    {"label": "is_article_2", "value": "is_article_2"},
                    {"label": "is_auto_consumption", "value": "is_auto_consumption"},
                    {"label": "is_article_4", "value": "is_article_4"},
                    {"label": "measure_reference_point", "value": "measure_reference_point"},
                    # transport.data.gouv.fr data
                    {"label": "station_name", "value": "station_name"},
                    {"label": "station_id", "value": "station_id"},
                ],
            }
        ],
    )
