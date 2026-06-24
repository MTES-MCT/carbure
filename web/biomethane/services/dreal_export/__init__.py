"""Flat Excel export of validated biomethane annual declarations for DREAL.

Package layout:
- columns.py: column registry (model fields and computed values), section colors
- context.py: bulk preload of declarations and related objects per producer
- metrics/: aggregated values (supply plan tonnage, etc.)
- export.py: xlsxwriter orchestration (one row per producer)

To add a computed column:
1. Add a color key in SECTION_COLORS (columns.py) if it belongs to a new section
2. Add or extend a preload function in metrics/ and wire it in load_export_context()
3. Expose the value on ExportRowContext and register a ColumnDef in build_column_defs()
"""

from .export import generate_dreal_export

__all__ = ["generate_dreal_export"]
