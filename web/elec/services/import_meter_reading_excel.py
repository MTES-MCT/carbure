import pandas as pd
from typing import Iterable
from django.core.files.uploadedfile import UploadedFile
from core.excel import ExcelError, TableParser
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.create_meter_reading_excel import get_previous_readings_by_charge_point

EXCEL_COLUMNS = {
    "charge_point_id": TableParser.id,
    "last_extracted_energy": TableParser.float,
    "extracted_energy": TableParser.float,
    "reading_date": TableParser.date,
}


class ExcelMeterReadingError:
    INVALID_METER_READING_DATA = "INVALID_METER_READING_DATA"
    CHARGE_POINT_NOT_REGISTERED = "CHARGE_POINT_NOT_REGISTERED"
    EXTRACTED_ENERGY_LOWER_THAN_BEFORE = "EXTRACTED_ENERGY_LOWER_THAN_BEFORE"


def import_meter_reading_excel(
    excel_file: UploadedFile,
    existing_charge_points: Iterable[ElecChargePoint],
    previous_application: ElecMeterReadingApplication = None,
    renewable_share: int = 1,
):
    valid_meter_readings = []
    validation_errors = []

    # get the primary keys of the charge points saved inside the DB
    charge_point_pks_by_id = {cp.charge_point_id: cp.pk for cp in existing_charge_points}

    # make sure we use the previous readings stored in the DB rather than the one sent inside the excel file
    previous_readings_by_charge_point = get_previous_readings_by_charge_point(existing_charge_points, previous_application)

    # parse the excel file with pandas
    meter_readings_data = pd.read_excel(excel_file, usecols=list(range(0, 4)))
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

    # check if the imported readings have errors, and save the correct ones
    for line, reading in enumerate(meter_readings_data.to_dict(orient="records"), 2):
        charge_point_id = reading["charge_point_id"]
        charge_point_pk = charge_point_pks_by_id.get(charge_point_id)
        extracted_energy = reading["extracted_energy"]
        previous_extracted_energy = previous_readings_by_charge_point.get(charge_point_id) or 0
        reading_date = reading["reading_date"]

        if charge_point_id not in charge_point_pks_by_id:
            error = ExcelError(ExcelMeterReadingError.CHARGE_POINT_NOT_REGISTERED, line=line, meta=charge_point_id)  # fmt: skip
            validation_errors.append(error)
        elif extracted_energy < previous_extracted_energy:
            error = ExcelError(ExcelMeterReadingError.EXTRACTED_ENERGY_LOWER_THAN_BEFORE, line=line, meta=charge_point_id)  # fmt: skip
            validation_errors.append(error)
        else:
            valid_meter_readings.append(
                {
                    "charge_point_id": charge_point_pk,
                    "extracted_energy": extracted_energy,
                    "renewable_energy": (extracted_energy - previous_extracted_energy) * renewable_share,
                    "reading_date": reading_date,
                }
            )

    errors = sorted(excel_errors + validation_errors, key=lambda e: e["line"])
    return valid_meter_readings, errors
