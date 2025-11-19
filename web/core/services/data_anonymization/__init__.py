"""
Module d'anonymisation des données - Structure modulaire.

Ce module contient :
- La classe de base Anonymizer
- Les anonymiseurs spécialisés par domaine (entities, users, etc.)
- Les fonctions utilitaires pour l'anonymisation
"""

from .base import Anonymizer
from .entities import EntityAnonymizer
from .users import UserAnonymizer
from .utils import anonymize_fields_and_collect_modifications, set_field_if_has_value, strikethrough
from .data_anonymization import BATCH_SIZE, DataAnonymizationService
