from unittest import TestCase

from doublecount.parser.helpers import to_upper_snake_case


class ToUpperSnakeCaseTest(TestCase):
    def test_converts_labels_to_upper_snake_case(self):
        self.assertEqual(to_upper_snake_case("Déchets industriels"), "DECHETS_INDUSTRIELS")
        self.assertEqual(to_upper_snake_case("Huiles ou graisses animales (C II)"), "HUILES_OU_GRAISSES_ANIMALES_C_II")
        self.assertEqual(to_upper_snake_case("camelCase / déjà--vu"), "CAMEL_CASE_DEJA_VU")
