from datetime import datetime

from django.db.models.query_utils import Q
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from certificates.serializers import DoubleCountingRegistrationPublicSerializer


class AgreementPublicListActionMixin:
    @extend_schema(
        responses=DoubleCountingRegistrationPublicSerializer(many=True),
    )
    @action(methods=["get"], detail=False, url_path="agreement-public")
    def agreements_public_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        year = datetime.now().year
        agreements_active = (
            queryset.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
            .select_related("production_site")
            .order_by("production_site__name")
        )

        active_agreements = DoubleCountingRegistrationPublicSerializer(agreements_active, many=True).data

        return Response(active_agreements)
