import unicodedata


# transform a string into a standard form in lower case without accents
def normalize_string(input_str: str):
    lower_case = (input_str or "").strip().lower()
    nfkd_form = unicodedata.normalize("NFKD", lower_case)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii
