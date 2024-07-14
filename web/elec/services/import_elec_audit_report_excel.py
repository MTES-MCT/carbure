import pandas as pd
from django import forms
from django.core.files.uploadedfile import UploadedFile

from core.utils import Validator, is_true
from elec.models.elec_charge_point import ElecChargePoint


class ExcelElecAuditReportError:
    INVALID_METER_READING_DATA = "INVALID_METER_READING_DATA"
    CHARGE_POINT_NOT_REGISTERED = "CHARGE_POINT_NOT_REGISTERED"
    EXTRACTED_ENERGY_LOWER_THAN_BEFORE = "EXTRACTED_ENERGY_LOWER_THAN_BEFORE"


def import_elec_audit_report_excel(
    excel_file: UploadedFile,
):
    report_data = ExcelElecAuditReport.parse_audit_report_excel(excel_file)
    return ExcelElecAuditReportValidator.bulk_validate(report_data)  # fmt:skip


class ExcelElecAuditReport:
    EXCEL_COLUMNS = [
        "charge_point_id",
        "",
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
        meter_readings_data["line"] = meter_readings_data.index + 1  # add a line number to locate data in the excel file
        meter_readings_data.rename(columns={meter_readings_data.columns[i]: column for i, column in enumerate(ExcelElecAuditReport.EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
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
