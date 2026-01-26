"""
Anonymization module - Modular structure.

  This module contains:
  - The base Anonymizer class
  - The specialized anonymizers by domain (entities, users, etc.)
  - The utility functions for anonymization
"""

from .anonymizers.base import Anonymizer
from .anonymizers.entities import EntityAnonymizer
from .anonymizers.users import UserAnonymizer
from .utils import anonymize_fields_and_collect_modifications, set_field_if_has_value
from .data_anonymization import BATCH_SIZE, DataAnonymizationService
