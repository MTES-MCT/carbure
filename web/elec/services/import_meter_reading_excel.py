from typing import Iterable
import pandas as pd
from django.core.files.uploadedfile import UploadedFile
from core.excel import ExcelError, TableParser
from elec.models.elec_charge_point import ElecChargePoint

EXCEL_COLUMNS = {
    "charge_point_id": TableParser.id,
    "last_extracted_energy": TableParser.float,
    "extracted_energy": TableParser.float,
}


class ExcelMeterReadingError:
    INVALID_METER_READING_DATA = "INVALID_METER_READING_DATA"
    CHARGE_POINT_NOT_REGISTERED = "CHARGE_POINT_NOT_REGISTERED"
    EXTRACTED_ENERGY_LOWER_THAN_BEFORE = "EXTRACTED_ENERGY_LOWER_THAN_BEFORE"


def import_meter_reading_excel(excel_file: UploadedFile, existing_charge_points):
    meter_readings_data = pd.read_excel(excel_file, usecols=list(range(0, 3)))
    meter_readings_data["line"] = meter_readings_data.index  # add a line number to locate data in the excel file
    meter_readings_data.rename(columns={meter_readings_data.columns[i]: column for i, column in enumerate(EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
    meter_readings_data.dropna(inplace=True)
    meter_readings_data, parse_errors = TableParser.parse_columns(meter_readings_data, EXCEL_COLUMNS)

    excel_errors = [
        ExcelError(
            ExcelMeterReadingError.INVALID_METER_READING_DATA,
            line=meter_readings_data.loc[error["row"]]["line"],
            meta=error["column"],
        )
        for error in parse_errors
    ]

    meter_readings = meter_readings_data.to_dict(orient="records")

    valid_meter_readings = []
    validation_errors = []

    charge_points_by_id = {cp.charge_point_id: cp.id for cp in existing_charge_points}

    for line, reading in enumerate(meter_readings, 2):
        if reading["charge_point_id"] not in charge_points_by_id:
            error = ExcelError(ExcelMeterReadingError.CHARGE_POINT_NOT_REGISTERED, line=line, meta=reading["charge_point_id"])  # fmt: skip
            validation_errors.append(error)
        if reading["extracted_energy"] < reading["last_extracted_energy"]:
            error = ExcelError(ExcelMeterReadingError.EXTRACTED_ENERGY_LOWER_THAN_BEFORE, line=line, meta=reading["charge_point_id"])  # fmt: skip
            validation_errors.append(error)
        else:
            reading_data = {
                "charge_point_id": charge_points_by_id[reading["charge_point_id"]],
                "extracted_energy": reading["extracted_energy"],
            }
            valid_meter_readings.append(reading_data)

    errors = sorted(excel_errors + validation_errors, key=lambda e: e["line"])
    return valid_meter_readings, errors
