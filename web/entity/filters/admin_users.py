from django_filters import FilterSet, MultipleChoiceFilter, OrderingFilter

from core.filters import MultipleBooleanFilter
from core.models import Entity, UserRights


class AdminUserFilter(FilterSet):
    entity_type = MultipleChoiceFilter(field_name="entity__entity_type", choices=Entity.ENTITY_TYPES)
    role = MultipleChoiceFilter(field_name="role", choices=UserRights.ROLES)
    is_active = MultipleBooleanFilter(field_name="user__is_active")
    order_by = OrderingFilter(
        fields=(
            ("entity__name", "entity_name"),
            ("entity_id", "entity_id"),
            ("user__email", "user"),
            ("role", "role"),
            ("user__is_active", "is_active"),
        )
    )

    class Meta:
        model = UserRights
        fields = []
