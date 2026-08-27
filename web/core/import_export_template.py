import re
from typing import NotRequired, TypedDict

import xlsxwriter
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import path, reverse
from import_export.admin import ImportExportModelAdmin

from core.excel import ExcelResponse

HEADER_ROW = 1
DATA_START_ROW = 2
DATA_START_ROW_WITH_COMMENTS = 3


class TemplateColumns(TypedDict):
    header: str
    options: NotRequired[list]
    comment: NotRequired[str]
    color: NotRequired[str]


class ImportExportWithTemplateModelAdmin(ImportExportModelAdmin):
    """
    Generate an admin page with django-import-export and the ability to generate a template file.

    Usage:

    @admin.register(MyModel)
    class MyModelAdmin(ImportExportWithTemplateModelAdmin):
        import_template_columns=[
            {
                "header": "my_other_model",
                "options": MyOtherModel.objects.order_by("name").values_list("name", flat=True),
            },
            {
                "header": "my_string_value",
                "options": ["One", "Two"],
            },
        ]
    )
    """

    import_template_name = "admin/import_export/import_with_template_download.html"
    import_template_columns: list[TemplateColumns] = None
    import_template_title = None

    def get_import_context_data(self, **kwargs):
        context = super().get_import_context_data(**kwargs)
        context["import_template_download_url"] = self.get_import_template_download_url()
        return context

    def get_import_template_title(self):
        if self.import_template_title:
            return self.import_template_title
        return self.model._meta.verbose_name

    def get_import_template_columns(self):
        columns = self.import_template_columns or []
        resolved_columns = []
        for spec in columns:
            options = spec.get("options", [])
            if isinstance(options, QuerySet):
                options = options.all()
            resolved_columns.append({**spec, "options": options})
        return resolved_columns

    def get_import_template_url_name(self):
        app_label, model_name = self.get_model_info()
        return f"{app_label}_{model_name}_import_template"

    def get_import_template_download_url(self):
        if not self.get_import_template_columns():
            return None
        return reverse(
            f"admin:{self.get_import_template_url_name()}",
            current_app=self.admin_site.name,
        )

    def get_urls(self):
        urls = super().get_urls()
        if not self.get_import_template_columns():
            return urls
        return [
            path(
                "import-template/",
                self.admin_site.admin_view(self.import_template_view),
                name=self.get_import_template_url_name(),
            ),
            *urls,
        ]

    def import_template_view(self, request):
        if not self.has_import_permission(request):
            raise PermissionDenied
        return ExcelResponse(
            create_import_template(
                title=self.get_import_template_title(),
                columns=self.get_import_template_columns(),
            )
        )


def get_data_start_row(columns: list[TemplateColumns]) -> int:
    if any(spec.get("comment") for spec in columns):
        return DATA_START_ROW_WITH_COMMENTS
    return DATA_START_ROW


def _cell_format(workbook, color=None, **props):
    # Excel hides gridlines on filled cells; a thin border keeps the rows visible.
    if color:
        props["bg_color"] = color
        props.setdefault("border", 1)
        props.setdefault("border_color", "#B4B4B4")
    return workbook.add_format(props)


def _formats_for_column(workbook, color=None):
    """Header, hint row and data cells of a column share the same fill color."""
    return {
        "header": _cell_format(workbook, color, bold=True, text_wrap=True, valign="vcenter"),
        "comment": _cell_format(workbook, color, italic=True, font_color="#000000", text_wrap=True),
        "column": _cell_format(workbook, color) if color else None,
    }


def _write_column(sheet, col, spec, formats, has_comments):
    sheet.write(HEADER_ROW - 1, col, spec["header"], formats["header"])
    sheet.set_column(col, col, 35, formats["column"])
    if has_comments:
        sheet.write(DATA_START_ROW - 1, col, spec.get("comment", ""), formats["comment"])


def _add_dropdown(main_sheet, reference_sheet, col, spec, first_data_row):
    """List options live on the hidden References sheet and feed the column dropdown."""
    options = spec.get("options") or []
    reference_sheet.write(0, col, spec["header"])
    for row, value in enumerate(options, start=1):
        reference_sheet.write(row, col, value)

    if not options:
        return

    column_letter = chr(ord("A") + col)
    main_sheet.data_validation(
        f"{column_letter}{first_data_row}:{column_letter}1000",
        {
            "validate": "list",
            "source": f"=References!${column_letter}$2:${column_letter}${len(options) + 1}",
        },
    )


def create_import_template(title: str, columns: list[TemplateColumns]):
    path = f"/tmp/{to_snake_case(title)}_import_template.xlsx"
    workbook = xlsxwriter.Workbook(path)
    main_sheet = workbook.add_worksheet(title)
    reference_sheet = workbook.add_worksheet("References")
    reference_sheet.hide()
    reference_sheet.protect()

    first_data_row = get_data_start_row(columns)
    has_comments = first_data_row == DATA_START_ROW_WITH_COMMENTS
    main_sheet.set_row(HEADER_ROW - 1, 24)
    if has_comments:
        main_sheet.set_row(DATA_START_ROW - 1, 36)

    for col, spec in enumerate(columns):
        formats = _formats_for_column(workbook, spec.get("color"))
        _write_column(main_sheet, col, spec, formats, has_comments)
        _add_dropdown(main_sheet, reference_sheet, col, spec, first_data_row)

    workbook.close()
    return open(path, "rb")


def to_snake_case(value: str) -> str:
    value = re.sub(r"[^\w\s]", "", value)
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_").lower()
