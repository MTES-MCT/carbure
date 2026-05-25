import re


class NationalTradeRegister:
    @staticmethod
    def from_id(ntr_id):
        country_code, _code_scheme, _code_scheme_end_mark, registration_id = (
            re.compile(r"([A-Z]{2})_([A-Z_]+)_(CD|MBN)(.+)").search(ntr_id).groups()
        )

        return NationalTradeRegister(country_code, registration_id)

    def __init__(self, country_code, registration_id):
        self.country_code = country_code
        self.registration_id = registration_id
