from django.http import JsonResponse
import pandas as pd
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Biocarburant, CarbureLot, MatierePremiere
from django.db.models.aggregates import Count, Sum

from doublecount.models import DoubleCountingProduction
from doublecount.serializers import BiofuelSerializer, FeedStockSerializer


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

    # return JsonResponse(
    #     {"status": "success", "data": DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data}
    # )

    quotas =  get_quotas_info(agreement)

    return SuccessResponse({ 
        "application" :DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data,
        "quotas" : get_quotas_info(agreement)
    })



def get_quotas_info(agreement: DoubleCountingRegistration):
    application = agreement.application
    # production = get_production_site_double_counting_production(agreement.production_site.id, agreement.valid_from.year)

    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    #tous les couples BC / MP pour le site de production sur une année
    detailed_quotas = DoubleCountingProduction.objects.values("biofuel", "feedstock", "approved_quota").filter(dca_id=application.id,approved_quota__gt=0)

    #tous les lots pour des MP double compté pour le site de production regroupé par couple et par année
    production_lots = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_production_site_id=application.production_site,
        )
        .values("year", "feedstock", "biofuel")
        # .values("year", "feedstock", "biofuel", "biofuel__masse_volumique")
        .filter(feedstock_id__in=feedstocks.keys())
        .annotate(production_volume=Sum("volume"), lot_count=Count("id"))
    )

    # crée un dataframe pour les quotas par couple et par année
    # application_data = pd.DataFrame(detailed_quotas.values('biofuel', 'feedstock'))
    quotas_df = pd.DataFrame(detailed_quotas).rename(columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"})

    # crée un dataframe pour le résumé des lots par couple et par année
    # production_lots_df = pd.DataFrame(production_lots).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id", "biofuel__masse_volumique": "masse_volumique"})
    production_lots_df = pd.DataFrame(production_lots).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id"})

    #merge les deux dataframes
    quotas_df.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    production_lots_df.set_index(["biofuel_id", "feedstock_id"], inplace=True)

    result_df = quotas_df.merge(production_lots_df, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
    result_df = result_df.loc[result_df['approved_quota'] > 0]

    result_df["feedstock"] = result_df["feedstock_id"].apply(lambda id: FeedStockSerializer(feedstocks[id]).data)
    result_df["biofuel"] = result_df["biofuel_id"].apply(lambda id: BiofuelSerializer(biofuels[id]).data)
    result_df["quotas_progress"] = round(result_df["production_volume"] / result_df["approved_quota"],2)
    # result_df["current_production_weight_sum_tonnes"] = (res["volume"] * res["masse_volumique"] / 1000).apply(
    #     lambda x: round(x, 2)
    # )



    return result_df.to_dict("records")


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
