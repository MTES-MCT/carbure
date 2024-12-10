from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    paragraph._element = paragraph._p = None


def replace_and_bold(paragraph, old_text, new_text, font_name="Times New Roman", font_size=12):
    for run in paragraph.runs:
        if old_text in run.text:
            parts = run.text.split(old_text)
            run.text = parts[0]

            new_run = paragraph.add_run(new_text)
            new_run.font.bold = True
            new_run.font.name = font_name
            new_run.font.size = Pt(font_size)
            new_run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)

            if len(parts) > 1:
                remaining_run = paragraph.add_run(parts[1])
                remaining_run.font.name = font_name
                remaining_run.font.size = Pt(font_size)
                remaining_run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)


def set_font(paragraph, font_name="Times New Roman", font_size=12, bold=None):
    for run in paragraph.runs:
        run.font.name = font_name
        run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
        run.font.size = Pt(font_size)
        if bold:
            run.font.bold = bold


def set_bold_text(paragraph, text):
    paragraph.clear()
    run = paragraph.add_run(text)
    run.bold = True


def set_cell_border(cell, border_color="000000", border_size="4"):
    tc_pr = cell._element.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for border_name in ["top", "bottom", "left", "right"]:
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), border_size)
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), border_color)
        borders.append(border)
    tc_pr.append(borders)


class DoubleCountingApplicationExportError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    APPLICATION_NOT_ACCEPTED = "APPLICATION_NOT_ACCEPTED"
    DECHETS_INDUSTRIELS_NOT_FOUND = "DECHETS_INDUSTRIELS_NOT_FOUND"


class WordKey:
    CITY = "«Ville»"
    COUNTRY = "«Pays»"
    OPERATOR_NAME = "«Nom_Opérateur»"
    ADDRESS = "«Adresse»"
    POSTAL_CODE = "«Code_Postal»"
    CERTIFICATE_ID = "«Numéro_valide»"
    YEAR_N = "«Année n»"
    YEAR_N_1 = "«Année n+1»"
    ID = "«ID»"
    DECHETS_INDUSTRIELS = "«DECHETS_INDUSTRIELS»"
    BIOFUELS = "«YYYY»"


def application_to_json(application, dechets_industriels="-"):
    year_n = application.period_start.year
    year_n_1 = year_n + 1
    has_dechets_industriels = check_has_dechets_industriels(application)
    biofuels = list(
        application.production.filter(year__in=[year_n, year_n_1]).values_list("biofuel__name", flat=True).distinct()
    )

    return {
        "id": str(application.id),
        "city": application.production_site.city,
        "country": application.production_site.country.name,
        "name": application.production_site.name,
        "certificate_id": application.certificate_id,
        "addresse": application.production_site.address,
        "postal_code": str(application.production_site.postal_code),
        "year_n": str(application.period_start.year),
        "year_n_1": str(application.period_start.year + 1),
        "has_dechets_industriels": has_dechets_industriels,
        "dechets_industriels": dechets_industriels,
        "biofuels": format_biofuels_to_text(biofuels),
    }


def format_to_word(data):
    return {
        WordKey.CITY: data.get("city"),
        WordKey.COUNTRY: data.get("country"),
        WordKey.OPERATOR_NAME: data.get("name"),
        WordKey.ADDRESS: data.get("addresse"),
        WordKey.POSTAL_CODE: data.get("postal_code"),
        WordKey.CERTIFICATE_ID: data.get("certificate_id"),
        WordKey.YEAR_N: data.get("year_n"),
        WordKey.YEAR_N_1: data.get("year_n_1"),
        WordKey.ID: data.get("id"),
        WordKey.BIOFUELS: data.get("biofuels"),
        WordKey.DECHETS_INDUSTRIELS: data.get("dechets_industriels").lower(),
    }


def format_biofuels_to_text(biofuels):
    if not biofuels:
        return ""
    if len(biofuels) == 1:
        return f"des {biofuels[0]}".lower()
    elif len(biofuels) == 2:
        return f"des {biofuels[0]} et des {biofuels[1]}".lower()
    else:
        return f"des {', des '.join(biofuels[:-1])} et des {biofuels[-1]}".lower()


def check_has_dechets_industriels(application):
    return application.production.filter(feedstock__code="DECHETS_INDUSTRIELS").exists()
