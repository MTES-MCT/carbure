from pathlib import Path

from core.models import StoredFile

ACTION_IMPORT_UPLOAD_DIR = "traceability/actions"


def store_action_import_file(uploaded_file, *, entity, user) -> StoredFile:
    uploaded_file.seek(0)
    stored_file = StoredFile(
        name=Path(getattr(uploaded_file, "name", "") or "import.xlsx").name,
        url=uploaded_file,
        entity=entity,
        user=user,
    )
    stored_file.upload_to_dir = ACTION_IMPORT_UPLOAD_DIR
    stored_file.save()
    return stored_file
