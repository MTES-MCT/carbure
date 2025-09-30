import pandas as pd


class ExcelValidationError(Exception):
    """Exception raised when Excel data validation fails"""

    def __init__(self, validation_errors, total_rows_processed):
        self.validation_errors = validation_errors
        self.total_rows_processed = total_rows_processed
        super().__init__("Excel validation failed")


class ExcelImporter:
    @staticmethod
    def parse(file, header_row=0, sheet_name=None):
        """
        Parse an Excel file and return data as a list of dictionaries.

        Args:
            file: Excel file to parse
            header_row: Row to use as headers (int or string)
            sheet_name: Sheet name (None for first sheet)

        Returns:
            List of dictionaries representing rows
        """
        df = pd.read_excel(file, header=header_row, sheet_name=sheet_name)

        return df.to_dict(orient="records")

    @staticmethod
    def validate_retrieved_data(data, serializer_class, config):
        """
        Validate data using the provided serializer class.

        Args:
            data: List of dictionaries to validate
            serializer_class: DRF serializer class to use for validation
            config: Configuration dict containing header_row info

        Returns:
            List of valid serializer instances

        Raises:
            ExcelValidationError: If validation errors are found
        """
        # Collect all validation errors by row
        validation_errors = []
        valid_instances = []

        for row_index, row in enumerate(data, start=1):
            input_serializer = serializer_class(data=row)

            if input_serializer.is_valid():
                valid_instances.append(input_serializer)
            else:
                # Add row number to errors
                excel_row_number = row_index + config["header_row"] + 1
                validation_errors.append(
                    {
                        "row": excel_row_number,
                        "errors": input_serializer.errors,
                    }
                )

        # If there are validation errors, raise exception
        if validation_errors:
            raise ExcelValidationError(validation_errors, len(data))

        # If all validations passed
        return valid_instances
