import re
from typing import NotRequired, TypedDict

import xlsxwriter
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.urls import path, reverse
from import_export.admin import ImportExportModelAdmin

from core.excel import ExcelResponse


class TemplateColumns(TypedDict):
    header: str
    options: NotRequired[list]


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


def create_import_template(title: str, columns: list[TemplateColumns]):
    path = f"/tmp/{to_snake_case(title)}_import_template.xlsx"
    workbook = xlsxwriter.Workbook(path)

    # Create the main sheet
    main_sheet = workbook.add_worksheet(title)

    headers = [c["header"] for c in columns]
    header_format = workbook.add_format({"bold": True, "text_wrap": True, "valign": "vcenter"})

    main_sheet.set_row(0, 24)
    for col, header in enumerate(headers):
        main_sheet.write(0, col, header, header_format)
        main_sheet.set_column(col, col, 35)

    # Create the reference sheet for dropdowns
    reference_sheet = workbook.add_worksheet("References")
    for col, spec in enumerate(columns):
        reference_sheet.write(0, col, spec["header"])
        options = spec.get("options", [])
        for row, value in enumerate(options, start=1):
            reference_sheet.write(row, col, value)

    reference_sheet.hide()
    reference_sheet.protect()

    # Add the validation rules to enable dropdowns
    for col, spec in enumerate(columns):
        options = spec.get("options", [])
        if not options:
            continue

        column_letter = chr(ord("A") + col)  # get the column letter based on index
        max_row = len(options) + 1

        main_sheet.data_validation(
            f"{column_letter}2:{column_letter}1000",
            {
                "validate": "list",
                "source": f"=References!${column_letter}$2:${column_letter}${max_row}",
            },
        )

    workbook.close()
    return open(path, "rb")


def to_snake_case(value: str) -> str:
    value = re.sub(r"[^\w\s]", "", value)
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_").lower()
