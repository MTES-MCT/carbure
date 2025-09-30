import pandas as pd


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
