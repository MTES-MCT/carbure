import os
import tempfile

from django.test import SimpleTestCase

from core.excel import ExcelResponse


class ExcelResponseTest(SimpleTestCase):
    def test_uses_basename_and_cleans_up_the_exported_file(self):
        excel_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        file_path = excel_file.name
        excel_file.write(b"excel")
        excel_file.seek(0)

        response = ExcelResponse(excel_file)

        self.assertEqual(
            response["Content-Disposition"],
            f'attachment; filename="{os.path.basename(file_path)}"',
        )
        self.assertTrue(excel_file.closed)
        self.assertFalse(os.path.exists(file_path))
