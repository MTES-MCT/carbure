"""Flat Excel export of validated biomethane annual declarations for DREAL.

Package layout:
- columns.py: column registry (model fields and computed values), section colors
- context.py: bulk preload of declarations and related objects per producer
- export.py: xlsxwriter orchestration (one row per producer)

To add a computed column:
1. Add a color key in SECTION_COLORS (columns.py) if it belongs to a new section
2. Extend ExportRowContext and preload the data in load_export_context() (context.py)
3. Register a ColumnDef in build_column_defs() (columns.py)
"""

from .export import generate_dreal_export

__all__ = ["generate_dreal_export"]
