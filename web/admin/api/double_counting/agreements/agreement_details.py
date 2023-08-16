from django.http import JsonResponse
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.common import ErrorResponse
from core.decorators import check_admin_rights
from core.models import CarbureLot, MatierePremiere
from django.db.models.aggregates import Count, Sum


class DoubleCountingAgreementError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"


@check_admin_rights()
def get_agreement_details(request, *args, **kwargs):
    agreement_id = request.GET.get("agreement_id", None)

    if not agreement_id:
        return ErrorResponse(400, DoubleCountingAgreementError.MALFORMED_PARAMS)

    agreement = DoubleCountingRegistration.objects.get(id=agreement_id)

    # production = get_production_site_double_counting_production(agreement.production_site.id, agreement.valid_from.year)

    return JsonResponse(
        {"status": "success", "data": DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data}
    )


def get_production_site_double_counting_production(production_site_id, first_year):
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    double_counting_production = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_production_site_id=production_site_id,
            year_in=[first_year, first_year + 1],
        )
        .values("year", "feedstock", "biofuel", "biofuel__masse_volumique")
        .filter(feedstock_id__in=feedstocks.keys())
        .annotate(volume=Sum("volume"), nb_lots=Count("id"))
    )
