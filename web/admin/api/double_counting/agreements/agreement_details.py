from pprint import pprint
from django.http import JsonResponse
import pandas as pd
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.common import ErrorResponse
from core.decorators import check_admin_rights
from core.models import Biocarburant, CarbureLot, MatierePremiere
from django.db.models.aggregates import Count, Sum

from doublecount.models import DoubleCountingProduction


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

    # return SuccessResponse({ 
    #     "application" :DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data,
    #     # "quotas" : get_quotas_info(agreement)
    # })



def get_quotas_info(agreement: DoubleCountingRegistration):
    application = agreement.application
    # production = get_production_site_double_counting_production(agreement.production_site.id, agreement.valid_from.year)

    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    detailed_quotas = DoubleCountingProduction.objects.all().filter(dca_id=application.id)
    print("detailed_quotas: ", detailed_quotas)
    production = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_production_site_id=application.production_site,
        )
        .values("year", "feedstock", "biofuel", "biofuel__masse_volumique")
        .filter(feedstock_id__in=feedstocks.keys())
        .annotate(volume=Sum("volume"), nb_lots=Count("id"))
    )

    pprint(production)

    # Merge both datasets
    application_data = pd.DataFrame(columns={"biofuel", "feedstock", "approved_quota"}, data=detailed_quotas).rename(
        columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"}
    )
    pprint(application_data)
    quotas_data = pd.DataFrame(
        columns={"feedstock", "biofuel", "volume", "nb_lots", "biofuel__masse_volumique"}, data=production
    ).rename(
        columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id", "biofuel__masse_volumique": "masse_volumique"}
    )
    pprint(quotas_data)
    # df1.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    # df2.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    # res = df1.merge(df2, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
    # res["feedstock"] = res["feedstock_id"].apply(lambda x: feedstocks[x].natural_key())
    # res["biofuel"] = res["biofuel_id"].apply(lambda x: biofuels[x].natural_key())
    # res["current_production_weight_sum_tonnes"] = (res["volume"] * res["masse_volumique"] / 1000).apply(
    #     lambda x: round(x, 2)
    # )

    result = [{
        "feedstock": "Huile alimentaire usagée",
        "biofuel": "Huiles Végétales Hydrotraitées - Kérosène",
        "production_volume": 30000,
        "approved_quota": 40000,
        "lot_count": 100,
        "quotas_progress": 0.75,
    }]

    return result


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
