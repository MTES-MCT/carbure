from django_filters import ChoiceFilter, FilterSet

from stock_poc.models import Action
from stock_poc.models.action_status import ActionStatus


class ActionFilter(FilterSet):
    type = ChoiceFilter(choices=Action.TYPES)
    status = ChoiceFilter(choices=ActionStatus.STATUSES)

    class Meta:
        model = Action
        fields = ["type", "status"]
