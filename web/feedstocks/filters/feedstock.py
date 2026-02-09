from django_filters import BooleanFilter, FilterSet


class FeedstockFilter(FilterSet):
    is_methanogenic = BooleanFilter(field_name="matiere_premiere__is_methanogenic", required=False)
    is_biofuel_feedstock = BooleanFilter(field_name="matiere_premiere__is_biofuel_feedstock", required=False)
