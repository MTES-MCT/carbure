from datetime import date
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from biomethane.factories.contract import BiomethaneContractFactory
from biomethane.models import BiomethaneContract
from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
from core.models import Department, Entity, ExternalAdminRights
from edelivery.ebms.ntr import NationalTradeRegister
from entity.factories.entity import EntityFactory
from entity.models import EntityScope


def create_entity_with_department(department, name="Entity", external_admin_right=ExternalAdminRights.DREAL):
    entity = EntityFactory.create(entity_type=Entity.EXTERNAL_ADMIN, name=name)
    dept_ct = ContentType.objects.get_for_model(Department)
    EntityScope.objects.create(entity=entity, content_type=dept_ct, object_id=department.id)
    ExternalAdminRights.objects.create(entity=entity, right=external_admin_right)
    return entity


class EntityTest(TestCase):
    def setUp(self):
        self.patched_UserRights = patch("core.models.entity.UserRights").start()
        self.dept_01 = Department.objects.create(code_dept="01", name="Ain")
        self.dept_02 = Department.objects.create(code_dept="02", name="Aisne")
        self.dept_03 = Department.objects.create(code_dept="03", name="Allier")
        self.entity = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
        self.production_unit = BiomethaneProductionUnit.objects.create(
            producer=self.entity, name="Test Production Unit", department=self.dept_02
        )
        self.dreal = create_entity_with_department(self.dept_01, name="DREAL 01")
        self.dreal_other = create_entity_with_department(self.dept_02, name="DREAL 02")

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

    @patch("core.models.entity.Entity.objects.filter")
    def test_fetches_entity_from_ntr_id(self, patched_filter):
        entity = Entity(id=12345)
        patched_last = patched_filter.return_value.last
        patched_last.return_value = entity

        patched_filter.assert_not_called()
        patched_last.assert_not_called()

        ntr = NationalTradeRegister.from_id("FR_SIREN_CD123456789")
        result = Entity.from_national_trade_register(ntr)
        patched_filter.assert_called_with(registered_country__code_pays="FR", registration_id="123456789")
        patched_last.assert_called()
        self.assertEqual(12345, result.id)

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
        dreal_a = create_entity_with_department(self.dept_03, name="DREAL A")
        dreal_b = create_entity_with_department(self.dept_03, name="DREAL B")
        producer = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
        BiomethaneProductionUnit.objects.create(producer=producer, name="Unit", department=self.dept_03)

        result = producer.get_managing_external_admins()

        self.assertEqual(result, [dreal_a, dreal_b])

    @patch("biomethane.services.ademe.AdemeService.get_ademe_min_effective_year", return_value=2021)
    def test_get_allowed_entities_for_ademe_filters_to_ademe_eligible_producers(self, _):
        ademe = create_entity_with_department(self.dept_02, external_admin_right=ExternalAdminRights.ADEME)
        producer_with_ademe_contract = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER, name="Producer ADEME")
        producer_without_ademe_contract = EntityFactory.create(
            entity_type=Entity.BIOMETHANE_PRODUCER, name="Producer non ADEME"
        )

        BiomethaneProductionUnit.objects.create(
            producer=producer_with_ademe_contract,
            name="Unit ADEME",
            department=self.dept_02,
        )
        BiomethaneProductionUnit.objects.create(
            producer=producer_without_ademe_contract,
            name="Unit non ADEME",
            department=self.dept_02,
        )

        BiomethaneContractFactory.create(
            producer=producer_with_ademe_contract,
            has_complementary_investment_aid=True,
            complementary_aid_organisms=[BiomethaneContract.COMPLEMENTARY_AID_ORGANISM_ADEME],
            effective_date=date(2021, 1, 1),
        )
        BiomethaneContractFactory.create(
            producer=producer_without_ademe_contract,
            complementary_aid_organisms=[],
            effective_date=date(2021, 1, 1),
        )

        allowed_entities = ademe.get_allowed_entities()

        self.assertIn(producer_with_ademe_contract, allowed_entities)
        self.assertNotIn(producer_without_ademe_contract, allowed_entities)
