import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_name(value):
    if not value:
        return

    # Pattern for letters, spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-ZÀ-ÿ\s\-']+$"

    if not re.match(pattern, value):
        raise ValidationError(
            _("Le nom ne peut contenir que des lettres, espaces, tirets (-) et apostrophes (')."),
            code="invalid_name_characters",
        )

    # Block names that consist only of spaces, hyphens, or apostrophes
    if re.match(r"^[\s\-']+$", value):
        raise ValidationError(_("Le nom doit contenir au moins une lettre."), code="name_no_letters")
