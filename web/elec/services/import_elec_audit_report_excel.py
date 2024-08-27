import pandas as pd
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from core.utils import Validator, is_true
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_charge_point import ElecChargePoint


def import_elec_audit_report_excel(excel_file: UploadedFile, audited_charge_points: QuerySet[ElecAuditChargePoint]):
    report_data = ExcelElecAuditReport.parse_audit_report_excel(excel_file)
    audited_charge_point_ids = audited_charge_points.values_list("charge_point__charge_point_id", flat=True)
    return ExcelElecAuditReportValidator.bulk_validate(report_data, {"audited_charge_point_ids": audited_charge_point_ids})


class ExcelElecAuditReport:
    EXCEL_COLUMNS = [
        "charge_point_id",
        "",  # DO NOT REMOVE: this column exists on the excel file, we just don't care about its content
        "observed_mid_or_prm_id",
        "is_auditable",
        "has_dedicated_pdl",
        "current_type",
        "audit_date",
        "observed_energy_reading",
        "comment",
    ]

    @staticmethod
    def parse_audit_report_excel(excel_file: UploadedFile):
        meter_readings_data = pd.read_excel(excel_file, usecols=list(range(3, 12)))
        meter_readings_data["line"] = meter_readings_data.index + 2  # add a line number to locate data in the excel file
        meter_readings_data.rename(
            columns={meter_readings_data.columns[i]: column for i, column in enumerate(ExcelElecAuditReport.EXCEL_COLUMNS)},
            inplace=True,
        )
        meter_readings_data = meter_readings_data.drop_duplicates("charge_point_id")
        meter_readings_data.dropna(inplace=True, how="all")
        meter_readings_data.fillna("", inplace=True)

        meter_readings_data["is_auditable"] = is_true(meter_readings_data, "is_auditable")
        meter_readings_data["has_dedicated_pdl"] = is_true(meter_readings_data, "has_dedicated_pdl")

        return meter_readings_data.to_dict(orient="records")


class ExcelElecAuditReportValidator(Validator):
    charge_point_id = forms.CharField()
    observed_mid_or_prm_id = forms.CharField(required=False, max_length=128)
    is_auditable = forms.BooleanField(required=False)
    has_dedicated_pdl = forms.BooleanField(required=False)
    current_type = forms.ChoiceField(required=False, choices=ElecChargePoint.CURRENT_TYPES)
    audit_date = forms.DateField(required=False, input_formats=Validator.DATE_FORMATS)
    observed_energy_reading = forms.FloatField(required=False, min_value=0)
    comment = forms.CharField(required=False, max_length=512)

    def extend(self, report):
        current_type = report.get("current_type")
        if current_type in ["AC", "CA"]:
            report["current_type"] = ElecChargePoint.AC
        elif current_type in ["DC", "CC"]:
            report["current_type"] = ElecChargePoint.DC
        else:
            report["current_type"] = None

        audit_date = report.get("audit_date")
        if audit_date is pd.NaT:
            report["audit_date"] = None

        observed_energy_reading = report.get("observed_energy_reading")
        if not observed_energy_reading:
            report["observed_energy_reading"] = 0

        return report

    def validate(self, audited_charge_point):
        charge_point_id = audited_charge_point.get("charge_point_id")
        expected_ids = self.context.get("audited_charge_point_ids")

        if charge_point_id not in expected_ids:
            self.add_error(
                "charge_point_id",
                _(
                    "Le point de charge {charge_point_id} ne fait pas partie de l'échantillon sélectionné pour cet audit."
                ).format(charge_point_id=charge_point_id),
            )
