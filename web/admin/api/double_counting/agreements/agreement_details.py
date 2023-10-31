from django.http import JsonResponse
import pandas as pd
from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import Biocarburant, CarbureLot, MatierePremiere
from django.db.models.aggregates import Count, Sum

from doublecount.models import DoubleCountingApplication, DoubleCountingProduction
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

    # return JsonResponse(
    #     {"status": "success", "data": DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data}
    # )

    result = DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data
    result["quotas"] = get_quotas_info(agreement)

    return SuccessResponse(result)


def get_quotas_info(agreement: DoubleCountingRegistration):
    application = agreement.application
    if not application or application.status != DoubleCountingApplication.ACCEPTED:
        return None

    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    # tous les couples BC / MP pour le site de production sur une année
    detailed_quotas = DoubleCountingProduction.objects.values("biofuel", "feedstock", "approved_quota", "year").filter(
        dca_id=application.id, approved_quota__gt=0
    )

    # tous les lots pour des MP double compté pour le site de production regroupé par couple et par année
    production_lots = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_production_site_id=application.production_site,
        )
        .values("year", "feedstock", "biofuel")
        .filter(feedstock_id__in=feedstocks.keys(), year__in=[agreement.valid_from.year, agreement.valid_from.year + 1])
        .annotate(production_kg=Sum("weight"), lot_count=Count("id"))
    )

    # crée un dataframe pour les quotas par couple et par année
    quotas_df = pd.DataFrame(detailed_quotas).rename(columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"})

    # crée un dataframe pour le résumé des lots par couple et par année
    production_lots_df = pd.DataFrame(production_lots).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id"})

    # merge les deux dataframes

    if len(production_lots_df) == 0:
        quotas_df["lot_count"] = 0
        quotas_df["production_tonnes"] = 0
        quotas_df["quotas_progression"] = 0
    else:
        quotas_df.set_index(["biofuel_id", "feedstock_id", "year"], inplace=True)
        production_lots_df.set_index(["biofuel_id", "feedstock_id", "year"], inplace=True)
        quotas_df = (
            quotas_df.merge(production_lots_df, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
        )
        quotas_df = quotas_df.loc[quotas_df["approved_quota"] > 0]
        quotas_df["production_tonnes"] = round(quotas_df["production_kg"] / 1000)
        quotas_df["quotas_progression"] = round((quotas_df["production_tonnes"] / quotas_df["approved_quota"]), 2)

    quotas_df["feedstock"] = quotas_df["feedstock_id"].apply(lambda id: FeedStockSerializer(feedstocks[id]).data)
    quotas_df["biofuel"] = quotas_df["biofuel_id"].apply(lambda id: BiofuelSerializer(biofuels[id]).data)

    del quotas_df["feedstock_id"]
    del quotas_df["biofuel_id"]
    return quotas_df.to_dict("records")
