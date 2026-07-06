from unittest import TestCase
from unittest.mock import patch

from core.models.entity import Entity


class EntityTest(TestCase):
    @patch("core.models.entity.Site")
    def test_knows_its_sites(self, patched_site):
        patched_filter = patched_site.objects.filter
        patched_filter.return_value = "some sites"

        entity = Entity()
        patched_filter.assert_not_called()

        result = entity.get_sites()
        patched_filter.assert_called_with(entitysite__entity=entity)
        self.assertEqual("some sites", result)
