import traceback
import pandas as pd
from django.core.files.uploadedfile import UploadedFile
from core.excel import TableParser
from elec.services.transport_data_gouv import TransportDataGouv


class ExcelChargePointError:
    EXCEL_PARSING_FAILED = "EXCEL_PARSING_FAILED"
    DUPLICATE_CHARGE_POINT = "DUPLICATE_CHARGE_POINT"
    MISSING_CHARGE_POINT_ID = "MISSING_CHARGE_POINT_ID"
    MISSING_CHARGE_POINT_IN_DATAGOUV = "MISSING_CHARGE_POINT_IN_DATAGOUV"
    MISSING_CHARGE_POINT_DATA = "MISSING_CHARGE_POINT_DATA"
    INVALID_CHARGE_POINT_DATA = "INVALID_CHARGE_POINT_DATA"


def import_charge_point_excel(excel_file: UploadedFile, existing_charge_points: list[str]):
    try:
        excel_data, excel_errors = ExcelChargePoints.parse_charge_point_excel(excel_file)
        transport_data = TransportDataGouv.find_charge_point_data(excel_data, 1000)
        valid_charge_points, validation_errors = ExcelChargePoints.validate_charge_points(excel_data, transport_data, existing_charge_points)  # fmt:skip
        errors = sorted(excel_errors + validation_errors, key=lambda e: e["line"])
        return valid_charge_points, errors
    except:
        traceback.print_exc()
        return [], [{"error": ExcelChargePointError.EXCEL_PARSING_FAILED}]


class ExcelChargePoints:
    EXCEL_COLUMNS = {
        "charge_point_id": TableParser.id,
        "installation_date": TableParser.date,
        "mid_id": TableParser.id,
        "measure_date": TableParser.date,
        "measure_energy": TableParser.float,
        "measure_reference_point_id": TableParser.id,
    }

    @staticmethod
    def parse_charge_point_excel(excel_file: UploadedFile):
        charge_point_data = pd.read_excel(excel_file, usecols=list(range(1, 11)))
        charge_point_data = charge_point_data.drop(charge_point_data.index[:11])
        charge_point_data = charge_point_data.dropna(how="all")  # remove completely empty rows
        charge_point_data["line"] = charge_point_data.index + 2  # add a line number to locate data in the excel file
        charge_point_data.rename(columns={charge_point_data.columns[i]: column for i, column in enumerate(ExcelChargePoints.EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
        charge_point_data = charge_point_data.reset_index(drop=True)

        if len(charge_point_data) >= 18:
            # default template example cells
            first_id = charge_point_data.at[0, "charge_point_id"]
            eighteenth_id = charge_point_data.at[17, "charge_point_id"]

            # the example was left in the template, so we skip it
            if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
                charge_point_data = charge_point_data.drop(charge_point_data.index[:19])
                charge_point_data = charge_point_data.reset_index(drop=True)

        charge_point_data, parse_errors = TableParser.parse_columns(charge_point_data, ExcelChargePoints.EXCEL_COLUMNS)

        errors = [
            Error(
                ExcelChargePointError.INVALID_CHARGE_POINT_DATA,
                line=charge_point_data.loc[error["row"]]["line"],
                meta=error["column"],
            )
            for error in parse_errors
        ]

        return charge_point_data.to_dict(orient="records"), errors

    @staticmethod
    def validate_charge_points(charge_points: list[dict], transport_data, existing_charge_points):
        valid_charge_points = []
        charge_points_errors = []

        transport_data_index = {row["charge_point_id"]: row for row in transport_data}

        for charge_point_data in charge_points:
            line = charge_point_data.pop("line")
            charge_point_id = charge_point_data["charge_point_id"]
            charge_point_transport_data = transport_data_index.get(charge_point_id)

            errors = []

            if not charge_point_id:
                errors.append(Error(ExcelChargePointError.MISSING_CHARGE_POINT_ID, line=line))
            elif charge_point_id in existing_charge_points:
                errors.append(Error(ExcelChargePointError.DUPLICATE_CHARGE_POINT, line=line, meta=charge_point_id))
            elif charge_point_transport_data is None:
                errors.append(Error(ExcelChargePointError.MISSING_CHARGE_POINT_IN_DATAGOUV, line=line, meta=charge_point_id))  # fmt:skip
            else:
                charge_point_data["station_id"] = charge_point_transport_data["station_id"]
                charge_point_data["station_name"] = charge_point_transport_data["station_name"]
                charge_point_data["nominal_power"] = charge_point_transport_data["nominal_power"]
                charge_point_data["current_type"] = charge_point_transport_data["current_type"]
                charge_point_data["is_article_2"] = charge_point_transport_data["is_article_2"]
                charge_point_data["cpo_name"] = charge_point_transport_data["cpo_name"]
                charge_point_data["cpo_siren"] = charge_point_transport_data["cpo_siren"]
                charge_point_data["latitude"] = charge_point_transport_data["latitude"]
                charge_point_data["longitude"] = charge_point_transport_data["longitude"]

                # si la data existe sur tdg, on vérifie les autres champs
                missing_fields = list(ExcelChargePoints.get_missing_fields(charge_point_data))

                if len(missing_fields) > 0:
                    errors += [
                        Error(ExcelChargePointError.MISSING_CHARGE_POINT_DATA, line=line, meta=field)
                        for field in missing_fields
                    ]

            if len(errors) > 0:
                charge_points_errors += errors
            else:
                valid_charge_points.append(charge_point_data)

        return valid_charge_points, charge_points_errors

    @staticmethod
    def get_missing_fields(charge_point):
        missing_fields = []

        if charge_point.get("is_article_2"):
            if not charge_point.get("measure_reference_point_id"):
                missing_fields.append("measure_reference_point_id")
        else:
            if not charge_point.get("mid_id"):
                missing_fields.append("mid_id")
            if not charge_point.get("measure_date"):
                missing_fields.append("measure_date")
            if not isinstance(charge_point.get("measure_energy"), float):
                missing_fields.append("measure_energy")

        return missing_fields


def Error(type: str, line: int, meta=None):
    error = {"line": int(line), "error": type}
    if meta is not None:
        error["meta"] = meta
    return error
