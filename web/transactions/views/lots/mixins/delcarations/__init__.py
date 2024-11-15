from .admin_declarations import DeclarationAdminMixin
from .declarations import DeclarationUserMixin
from .invalidate import InvalidateActionMixin
from .validate import ValidateDeclarationActionMixin


class DeclarationMixin(
    DeclarationAdminMixin,
    DeclarationUserMixin,
    InvalidateActionMixin,
    ValidateDeclarationActionMixin,
):
    pass
