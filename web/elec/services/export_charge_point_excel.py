import datetime

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
                    # {"label": "id", "value": "id"},
                    {"label": "Aménageur", "value": "cpo"},
                    # cpo excel data
                    {"label": "Identifiant du point de recharge", "value": "charge_point_id"},
                    {"label": "Type de courant", "value": "current_type"},
                    {"label": "Date d'installation date", "value": "installation_date"},
                    {"label": "Identifiant MID", "value": "mid_id"},
                    {"label": "Date du dernier relevé", "value": "measure_date"},
                    {"label": "Énergie mesurée lors du dernier relevé", "value": "measure_energy"},
                    # {"label": "is_article_2", "value": "is_article_2"},
                    # {"label": "is_auto_consumption", "value": "is_auto_consumption"},
                    # {"label": "is_article_4", "value": "is_article_4"},
                    {"label": "Identifiant du point de référence de mesure", "value": "measure_reference_point_id"},
                    # transport.data.gouv.fr data
                    {"label": "Nom de la station", "value": "station_name"},
                    {"label": "Identifiant de la station", "value": "station_id"},
                    {"label": "Puissance nominale", "value": "nominal_power"},
                    # {"label": "Latitude", "value": "latitude"},
                    # {"label": "Longitude", "value": "longitude"},
                    # {"label": "Nom de l'aménageur", "value": "cpo_name"},
                    # {"label": "SIREN de l'aménageur", "value": "cpo_siren"},
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
                "label": "Points de recharge à auditer",
                "rows": ElecChargePointSampleSerializer(charge_points, many=True).data,
                "columns": [
                    {"label": "Latitude", "value": "latitude"},
                    {"label": "Longitude", "value": "longitude"},
                    {"label": "Nom de la station", "value": "station_name"},
                    # {"label": "Identifiant de la station", "value": "station_id"},
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
