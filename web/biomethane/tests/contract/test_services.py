from django.test import TestCase

from biomethane.services.contract import BiomethaneContractService
from core.models import Entity


class BiomethaneContractServiceTests(TestCase):
    def setUp(self):
        self.producer_entity = Entity.objects.create(
            name="Test Producer",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

    def test_handle_is_red_ii_disables_when_cmax_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when cmax <= 200 and user wants to disable."""
        # Setup producer with Red II enabled
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": False,  # User wants to disable
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)
        self.assertNotIn("is_red_ii", validated_data)

    def test_handle_is_red_ii_disables_when_pap_below_threshold(self):
        """Test that handle_is_red_ii disables Red II when pap_contracted <= 19.5."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "pap_contracted": 15.0,  # Below threshold
            "is_red_ii": False,
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertFalse(self.producer_entity.is_red_ii)

    def test_handle_is_red_ii_no_change_when_above_threshold(self):
        """Test that handle_is_red_ii doesn't change Red II when values are above threshold."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 250.0,  # Above threshold
            "is_red_ii": False,  # User wants to disable but can't
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True

    def test_handle_is_red_ii_no_change_when_is_red_ii_not_false(self):
        """Test that handle_is_red_ii only acts when is_red_ii is explicitly False."""
        self.producer_entity.is_red_ii = True
        self.producer_entity.save()

        validated_data = {
            "cmax": 150.0,  # Below threshold
            "is_red_ii": True,  # User doesn't want to disable
        }

        BiomethaneContractService.handle_is_red_ii(validated_data, self.producer_entity)

        self.producer_entity.refresh_from_db()
        self.assertTrue(self.producer_entity.is_red_ii)  # Should remain True
