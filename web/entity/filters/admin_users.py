import re

from django_filters import CharFilter, FilterSet, MultipleChoiceFilter

from core.models import Entity, UserRights


class AdminUserFilter(FilterSet):
    entity_type = MultipleChoiceFilter(field_name="entity__entity_type", choices=Entity.ENTITY_TYPES)
    role = MultipleChoiceFilter(field_name="role", choices=UserRights.ROLES)
    user_ids = CharFilter(method="filter_user_ids")

    class Meta:
        model = UserRights
        fields = []

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        # django-filter only reads the query string. The pasted ids travel in the body.
        if request is not None and data is not None and "user_ids" not in data:
            raw = getattr(request, "data", {}).get("user_ids")
            if raw:
                data = data.copy()
                data["user_ids"] = raw
        super().__init__(data, queryset, request=request, prefix=prefix)

    def filter_user_ids(self, queryset, name, value):
        return queryset.filter(user_id__in=parse_user_ids(value))


def parse_user_ids(raw):
    return [int(token) for token in re.findall(r"\d+", raw or "")]
