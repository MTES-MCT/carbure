from math import prod
from core.decorators import check_admin_rights
from doublecount.parser.dc_parser import parse_dc_excel
from datetime import datetime

from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingAgreement,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from doublecount.helpers import (
    load_dc_filepath,
    load_dc_period,
    load_dc_sourcing_data,
    load_dc_production_data,
)
from core.models import Entity

from core.common import ErrorResponse, SuccessResponse

from django.db import transaction


class DoubleCountingAddError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PRODUCER_NOT_FOUND = "PRODUCER_NOT_FOUND"
    PRODUCTION_SITE_NOT_FOUND = "PRODUCTION_SITE_NOT_FOUND"
    PRODUCTION_SITE_ADDRESS_UNDEFINED = "PRODUCTION_SITE_ADDRESS_UNDEFINED"
    AGREEMENT_ALREADY_EXISTS = "AGREEMENT_ALREADY_EXISTS"


@check_admin_rights()
@transaction.atomic
def add_application(request, *args, **kwargs):
    producer_id = request.POST.get("producer_id", None)
    production_site_id = request.POST.get("production_site_id", None)
    file = request.FILES.get("file")

    if not production_site_id:
        return ErrorResponse(400, DoubleCountingAddError.MALFORMED_PARAMS)

    try:
        producer = Entity.objects.get(id=producer_id)
    except:
        return ErrorResponse(400, DoubleCountingAddError.PRODUCER_NOT_FOUND)

    try:
        production_site = ProductionSite.objects.get(producer_id=producer_id, id=production_site_id)
    except:
        return ErrorResponse(400, DoubleCountingAddError.PRODUCTION_SITE_NOT_FOUND)

    if not production_site.address:
        return ErrorResponse(400, DoubleCountingAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED)

    if file is None:
        return ErrorResponse(400, DoubleCountingAddError.MALFORMED_PARAMS)

    # 1 - load dc Data
    filepath = load_dc_filepath(file)

    info, sourcing_forecast_rows, production_max_rows, production_forecast_rows, requested_quota_rows = parse_dc_excel(
        filepath
    )

    start, end, _ = load_dc_period(info["start_year"])

    # check if agreement not rejected exists
    if DoubleCountingAgreement.objects.filter(
        producer=producer,
        period_start__year=start.year,
        status__in=[DoubleCountingAgreement.PENDING, DoubleCountingAgreement.REJECTED],
    ).exists():
        return ErrorResponse(400, DoubleCountingAddError.AGREEMENT_ALREADY_EXISTS)

    dca, _ = DoubleCountingAgreement.objects.get_or_create(
        producer=producer,
        production_site_id=production_site_id,
        period_start=start,
        period_end=end,
        defaults={"producer_user": request.user},
    )
    print("dca: ", dca)
    print("dca: ", dca.agreement_id)

    # 2 - save all production_data DoubleCountingProduction in db
    sourcing_forecast_data, _ = load_dc_sourcing_data(dca, sourcing_forecast_rows)
    production_data, _ = load_dc_production_data(dca, production_max_rows, production_forecast_rows, requested_quota_rows)
    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for sourcing in sourcing_forecast_data:
        sourcing.save()
    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for production in production_data:
        production.save()

    # try:
    #     send_dca_confirmation_email(dca)
    # except:
    #     print("email send error")
    #     traceback.print_exc()
    return SuccessResponse()


# def agreement_is_expired (dca) :
#     current_year = datetime.now().year
#     return dca.period_end < current_year
