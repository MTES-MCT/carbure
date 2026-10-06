from django_filters import FilterSet, MultipleChoiceFilter

from core.filters import MultipleBooleanFilter
from core.models import Entity, UserRights


class AdminUserFilter(FilterSet):
    entity_type = MultipleChoiceFilter(field_name="entity__entity_type", choices=Entity.ENTITY_TYPES)
    role = MultipleChoiceFilter(field_name="role", choices=UserRights.ROLES)
    is_active = MultipleBooleanFilter(field_name="user__is_active")

    class Meta:
        model = UserRights
        fields = []
