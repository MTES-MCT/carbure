import re


def from_national_trade_register(ntr):
    return re.compile(r"FR_SIREN_CD(\d{9})").search(ntr).group(1)
