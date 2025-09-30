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
        # Bulk validation
        serializer = serializer_class(data=data, many=True)

        if serializer.is_valid():
            return serializer
        else:
            validation_errors = []

            # serializer.errors is a list where each index corresponds to a data row
            starting_excel_row = 2 + config["header_row"]
            for row_index, row_errors in enumerate(serializer.errors, start=starting_excel_row):
                if row_errors:  # Only include rows with errors
                    excel_row_number = row_index
                    validation_errors.append(
                        {
                            "row": excel_row_number,
                            "errors": row_errors,
                        }
                    )

            raise ExcelValidationError(validation_errors, len(data))
