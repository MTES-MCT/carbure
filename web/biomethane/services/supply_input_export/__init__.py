"""Excel export of biomethane supply plan inputs (one row per feedstock line).

Package layout:
- columns.py: column registry for producer and DREAL variants
- export.py: serialize rows and delegate to core.excel.export_to_excel

To add a column:
1. Expose the value on BiomethaneSupplyInputExportSerializer (or nested objects)
2. Register the dotted path in BASE_COLUMNS or DREAL_PREFIX_COLUMNS
"""

from .export import generate_supply_input_export

__all__ = ["generate_supply_input_export"]
