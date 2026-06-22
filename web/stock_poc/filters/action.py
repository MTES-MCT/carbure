from django_filters import ChoiceFilter, FilterSet

from stock_poc.models import Action


class ActionFilter(FilterSet):
    type = ChoiceFilter(choices=Action.TYPES)
    status = ChoiceFilter(choices=Action.STATUSES)

    class Meta:
        model = Action
        fields = ["type", "status"]
