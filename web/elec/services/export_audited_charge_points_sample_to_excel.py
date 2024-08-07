import datetime
from core.excel import export_to_excel
from elec.serializers.elec_audit_charge_point import ElecAuditChargePointSerializer


def export_audited_charge_points_sample_to_excel(audited_charge_points, entity):
    today = datetime.date.today()
    file = "/tmp/charge_points_%s_sample_%s.xlsx" % (entity.slugify(), today.strftime("%Y-%m-%d_%H%M"))

    return export_to_excel(
        file,
        [
            {
                "label": "Points de recharge à auditer",
                "rows": ElecAuditChargePointSerializer(audited_charge_points, many=True).data,
                "columns": [
                    {"label": "Latitude", "value": "latitude"},
                    {"label": "Longitude", "value": "longitude"},
                    # {"label": "Nom de la station", "value": "station_name"},
                    {"label": "Identifiant de la station", "value": "station_id"},
                    {"label": "Identifiant du point de recharge", "value": "charge_point_id"},
                    {"label": "Identifiant PRM ou MID", "value": get_prm_or_mid},
                    {"label": "Identifiant PRM ou MID constaté (si différent)", "value": "observed_mid_or_prm_id"},
                    {"label": "Infrastructure de recharge installée à la localisation renseignée", "value": "is_auditable"},
                    {
                        "label": "Identifiant renseigné visible à proximité immédiate de l'infrastructure",
                        "value": "has_dedicated_pdl",
                    },
                    {"label": "Point de contrôle type de courant", "value": "current_type"},
                    {"label": "Date du relevé par l'intervenant", "value": "audit_date"},
                    {"label": "Énergie active totale relevée", "value": "observed_energy_reading"},
                    {"label": "Limite dans la mission de contrôle", "value": "comment"},
                ],
            }
        ],
        {"bold": True, "text_wrap": True, "align": "top"},
        column_width=13,
        header_height=60,
    )


def get_prm_or_mid(charge_point):
    charge_point = dict(charge_point)
    if charge_point.get("is_article_2"):
        return f"[PRM] {charge_point.get('measure_reference_point_id', 'N/A')}"
    else:
        return f"[MID] {charge_point.get('mid_id', 'N/A')}"
