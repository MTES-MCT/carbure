from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
from core.models import Department, Entity, ExternalAdminRights
from entity.factories.entity import EntityFactory
from entity.models import EntityScope


def create_dreal_entity_with_department(department):
    dreal = EntityFactory.create(entity_type=Entity.EXTERNAL_ADMIN)
    dept_ct = ContentType.objects.get_for_model(Department)
    EntityScope.objects.create(entity=dreal, content_type=dept_ct, object_id=department.id)
    ExternalAdminRights.objects.create(entity=dreal, right=ExternalAdminRights.DREAL)
    return dreal


class EntityTest(TestCase):
    def setUp(self):
        self.patched_UserRights = patch("core.models.UserRights").start()
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        self.dept_03 = Department.objects.create(code_dept="03", name="Allier")
        self.entity = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
        self.production_unit = BiomethaneProductionUnit.objects.create(
            producer=self.entity, name="Test Production Unit", department=self.dept_02
        )
        self.dreal = create_dreal_entity_with_department(self.dept_01)
        self.dreal_other = create_dreal_entity_with_department(self.dept_02)

    def tearDown(self):
        patch.stopall()

    def test_retrieves_its_admin_users(self):
        patched_filter = self.patched_UserRights.objects.filter
        patched_values_list = patched_filter.return_value.values_list

        entity = Entity()
        patched_filter.assert_not_called()
        patched_values_list.assert_not_called()

        entity.get_admin_users_emails()
        patched_filter.assert_called_with(entity=entity, role=self.patched_UserRights.ADMIN, user__is_active=True)
        patched_values_list.assert_called_with("user__email", flat=True)

    def test_get_managing_external_admins_returns_none_when_no_production_unit(self):
        """Sans unité de production, on ne récupère aucun admin."""
        producer_no_unit = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
        # Ne pas créer de BiomethaneProductionUnit pour cette entité
        result = producer_no_unit.get_managing_external_admins()

        self.assertIsNone(result)

    def test_get_managing_external_admins_returns_dreal_in_nominal_case(self):
        """Avec une unité de production et une DREAL sur ce département, on récupère cette DREAL."""
        # self.entity a une production_unit en dept_02, self.dreal_other est la DREAL du dept_02
        result = self.entity.get_managing_external_admins()

        self.assertIsNotNone(result)
        self.assertEqual(result, [self.dreal_other])

    def test_get_managing_external_admins_returns_both_dreals_when_same_department(self):
        """Deux DREALs reliées au même département : on récupère bien les deux."""
        dreal_a = create_dreal_entity_with_department(self.dept_03)
        dreal_b = create_dreal_entity_with_department(self.dept_03)
        producer = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
        BiomethaneProductionUnit.objects.create(producer=producer, name="Unit", department=self.dept_03)

        result = producer.get_managing_external_admins()

        self.assertEqual(result, [dreal_a, dreal_b])
