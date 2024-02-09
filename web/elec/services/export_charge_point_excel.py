import datetime

from openpyxl import Workbook

from core.excel import export_to_excel
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer, ElecChargePointSerializer


def export_charge_points_to_excel(charge_points, entity):
    today = datetime.date.today()
    file = "/tmp/charge_points_%s_%s.xlsx" % (entity.slugify(), today.strftime("%Y-%m-%d_%H%M"))

    return export_to_excel(
        file,
        [
            {
                "label": "Points de recharge",
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
                    {"label": "measure_reference_point_id", "value": "measure_reference_point_id"},
                    # transport.data.gouv.fr data
                    {"label": "station_name", "value": "station_name"},
                    {"label": "station_id", "value": "station_id"},
                    {"label": "nominal_power", "value": "nominal_power"},
                    {"label": "cpo_name", "value": "cpo_name"},
                    {"label": "cpo_siren", "value": "cpo_siren"},
                    {"label": "latitude", "value": "latitude"},
                    {"label": "longitude", "value": "longitude"},
                ],
            }
        ],
    )


def export_charge_points_sample_to_excel(charge_points, entity):
    today = datetime.date.today()
    file = "/tmp/charge_points_%s_sample_%s.xlsx" % (entity.slugify(), today.strftime("%Y-%m-%d_%H%M"))

    return export_to_excel(
        file,
        [
            {
                "label": "Échantillon à auditer",
                "rows": ElecChargePointSampleSerializer(charge_points, many=True).data,
                "columns": [
                    {"label": "Latitude", "value": "latitude"},
                    {"label": "Longitude", "value": "longitude"},
                    {"label": "Identifiant du point de recharge", "value": "charge_point_id"},
                    {"label": "Numéro du certificat d'examen du type", "value": "mid_id"},
                    {"label": "Infrastructure de recharge installée à la localisation renseignée", "value": ""},
                    {"label": "Identifiant renseigné visible à proximité immédiate de l'infrastructure", "value": ""},
                    {"label": "Point de contrôle type de courant", "value": ""},
                    {"label": "Numéro du certificat d'examen du type si différent", "value": ""},
                    {"label": "Date du relevé par l'intervenant", "value": ""},
                    {"label": "Énergie active totale relevée", "value": ""},
                    {"label": "Limite dans la mission de contrôle", "value": ""},
                ],
            }
        ],
        {"bold": True, "text_wrap": True, "align": "top"},
        column_width=13,
        header_height=60,
    )
