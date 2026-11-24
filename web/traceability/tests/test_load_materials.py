import os
import runpy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from feedstocks.models import Classification
from traceability.models import Material, MaterialTag
from traceability.models.material_tag import Tag


class LoadMaterialsTest(TestCase):
    def setUp(self):
        self.material = Material.objects.create(code="A", name="Alpha", unit=Material.KG)
        self.other = Material.objects.create(code="B", name="Beta", unit=Material.KG)
        MaterialTag.objects.create(material=self.material, type=Tag.INDUSTRY, value="H2")
        MaterialTag.objects.create(material=self.material, type=Tag.INDUSTRY, value="H2")
        MaterialTag.objects.create(material=self.other, type=Tag.INDUSTRY, value="H2")

    def load(self, csv_text):
        with TemporaryDirectory() as directory:
            fixture_dir = Path(directory) / "web/traceability/fixtures"
            fixture_dir.mkdir(parents=True)
            (fixture_dir / "materials.csv").write_text(csv_text, encoding="utf-8")
            with patch.dict(os.environ, {"CARBURE_HOME": directory}):
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "fixtures/load_materials.py"))

    def tags(self, material):
        return list(material.tags.order_by("value").values_list("type", "value"))

    def test_syncs_present_tag_columns_and_is_idempotent(self):
        original_tag_id = self.material.tags.order_by("id").first().id
        csv_text = "code,name,unit,industry\nA,Alpha,kg,H2 SB H2\n"
        self.load(csv_text)
        self.load(csv_text)
        self.assertEqual(self.tags(self.material), [(Tag.INDUSTRY, "H2"), (Tag.INDUSTRY, "SB")])
        self.assertEqual(self.material.tags.get(value="H2").id, original_tag_id)
        self.assertEqual(self.tags(self.other), [(Tag.INDUSTRY, "H2")])

        self.load("code,name,unit,industry\nA,Alpha,kg,SB\n")
        self.assertEqual(self.tags(self.material), [(Tag.INDUSTRY, "SB")])
        self.load("code,name,unit,industry\nA,Alpha,kg,\n")
        self.assertEqual(self.tags(self.material), [])

    def test_missing_tag_column_preserves_tags(self):
        self.load("code,name,unit\nA,Alpha,kg\n")
        self.assertEqual(self.tags(self.material), [(Tag.INDUSTRY, "H2"), (Tag.INDUSTRY, "H2")])
        self.assertEqual(self.tags(self.other), [(Tag.INDUSTRY, "H2")])

    def test_imports_and_clears_description(self):
        self.load("code,name,description,unit\nA,Alpha,Une description,kg\n")
        self.material.refresh_from_db()
        self.assertEqual(self.material.description, "Une description")

        self.load("code,name,description,unit\nA,Alpha,,kg\n")
        self.material.refresh_from_db()
        self.assertEqual(self.material.description, "")

    def test_imports_reuses_and_clears_category(self):
        existing = Classification.objects.create(group="", category="Bois", subcategory="")
        Classification.objects.create(group="Autre", category="Bois", subcategory="")
        csv_text = "code,name,unit,category\nA,Alpha,kg, Bois \nB,Beta,kg,Bois\n"
        self.load(csv_text)
        self.load(csv_text)
        self.material.refresh_from_db()
        self.other.refresh_from_db()
        self.assertEqual(self.material.classification, existing)
        self.assertEqual(self.other.classification, existing)
        self.assertEqual(Classification.objects.count(), 2)

        self.load("code,name,unit,category\nA,Alpha,kg,Nouvelle catégorie\n")
        self.material.refresh_from_db()
        self.assertEqual(self.material.classification.category, "Nouvelle catégorie")

        self.load("code,name,unit\nA,Alpha,kg\n")
        self.material.refresh_from_db()
        self.assertEqual(self.material.classification.category, "Nouvelle catégorie")

        self.load("code,name,unit,category\nA,Alpha,kg,\n")
        self.material.refresh_from_db()
        self.assertIsNone(self.material.classification)

    def test_failed_import_restores_materials_and_tags(self):
        with self.assertRaises(IntegrityError):
            self.load("code,name,unit,industry\nA,Nom modifié,kg,INVALID\n")

        self.material.refresh_from_db()
        self.assertEqual(self.material.name, "Alpha")
        self.assertEqual(self.tags(self.material), [(Tag.INDUSTRY, "H2"), (Tag.INDUSTRY, "H2")])
        self.assertEqual(self.tags(self.other), [(Tag.INDUSTRY, "H2")])
