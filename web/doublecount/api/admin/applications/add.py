import datetime
from django import forms
from django.core.mail import EmailMessage
from django.db.models import Q

import traceback
import os

import pytz
from carbure import settings
import unicodedata
import boto3
from certificates.models import DoubleCountingRegistration
from core.carburetypes import CarbureError
from core.decorators import check_admin_rights
from doublecount.parser.dc_parser import parse_dc_excel

from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingDocFile,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from doublecount.helpers import (
    load_dc_filepath,
    load_dc_period,
    load_dc_sourcing_data,
    load_dc_production_data,
)
from core.models import Entity, UserRights

from core.common import ErrorResponse, SuccessResponse

from django.db import transaction
from carbure.storage_backends import AWSStorage
from django.core.files.storage import FileSystemStorage


class DoubleCountingAdminAddFrom(forms.Form):
    producer_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.PRODUCER))
    should_replace = forms.BooleanField(required=False)
    producer_id = forms.ModelChoiceField(queryset=Entity.objects.filter(entity_type=Entity.PRODUCER))
    production_site_id = forms.ModelChoiceField(queryset=ProductionSite.objects.all())
    certificate_id = forms.CharField(required=False)


class DoubleCountingAddError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PRODUCTION_SITE_ADDRESS_UNDEFINED = "PRODUCTION_SITE_ADDRESS_UNDEFINED"
    APPLICATION_ALREADY_RECEIVED = "APPLICATION_ALREADY_RECEIVED"
    APPLICATION_ALREADY_EXISTS = "APPLICATION_ALREADY_EXISTS"
    AGREEMENT_ALREADY_EXISTS = "AGREEMENT_ALREADY_EXISTS"
    AGREEMENT_NOT_FOUND = "AGREEMENT_NOT_FOUND"
    MISSING_FILE = "MISSING_FILE"


@check_admin_rights()
@transaction.atomic
def add_application(request):
    form = DoubleCountingAdminAddFrom(request.POST)
    file = request.FILES.get("file")

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    producer: Entity = form.cleaned_data["producer_id"]
    should_replace: bool = form.cleaned_data["should_replace"]
    production_site: ProductionSite = form.cleaned_data["production_site_id"]
    certificate_id_to_link = form.cleaned_data["certificate_id"]

    if not production_site.address or not production_site.city or not production_site.postal_code:
        return ErrorResponse(400, DoubleCountingAddError.PRODUCTION_SITE_ADDRESS_UNDEFINED)

    if file is None:
        return ErrorResponse(400, DoubleCountingAddError.MISSING_FILE)

    # 1 - load dc Data
    filepath = load_dc_filepath(file)

    info, sourcing_forecast_rows, production_max_rows, production_forecast_rows, requested_quota_rows = parse_dc_excel(
        filepath
    )

    start, end, _ = load_dc_period(info["start_year"])

    # check if an application already exists for this producer, this period and is not accepted
    identical_replacable_application = DoubleCountingApplication.objects.filter(
        Q(production_site_id=production_site.id)
        & Q(period_start__year=start.year)
        & Q(status__in=[DoubleCountingApplication.PENDING, DoubleCountingApplication.REJECTED]),
    )

    if identical_replacable_application.exists():
        if should_replace:
            identical_replacable_application.delete()
        else:
            return ErrorResponse(400, DoubleCountingAddError.APPLICATION_ALREADY_EXISTS)

    # check if the agreement to link already exists
    if certificate_id_to_link:
        try:
            agreement = DoubleCountingRegistration.objects.get(certificate_id=certificate_id_to_link)
        except:
            return ErrorResponse(400, DoubleCountingAddError.AGREEMENT_NOT_FOUND)
    else:
        try:
            agreement = DoubleCountingRegistration.objects.get(
                production_site=production_site,
                valid_from=start,
            )
            return ErrorResponse(400, DoubleCountingAddError.AGREEMENT_ALREADY_EXISTS)
        except:
            agreement = None

    # create application
    dca, created = DoubleCountingApplication.objects.get_or_create(
        producer=producer,
        production_site_id=production_site.id,
        period_start=start,
        period_end=end,
        defaults={"producer_user": request.user},
    )

    if not created:
        return ErrorResponse(400, DoubleCountingAddError.APPLICATION_ALREADY_RECEIVED)

    if certificate_id_to_link:
        dca.certificate_id = certificate_id_to_link
        dca.save()
        agreement.application = dca
        agreement.save()

    # 2 - save all production_data DoubleCountingProduction in db
    sourcing_forecast_data, _ = load_dc_sourcing_data(dca, sourcing_forecast_rows)
    production_data, _ = load_dc_production_data(dca, production_max_rows, production_forecast_rows, requested_quota_rows)
    DoubleCountingSourcing.objects.filter(dca=dca).delete()
    for sourcing in sourcing_forecast_data:
        sourcing.save()
    DoubleCountingProduction.objects.filter(dca=dca).delete()
    for production in production_data:
        production.save()

    try:
        send_dca_confirmation_email(dca)
    except:
        print("email send error")
        traceback.print_exc()
    return SuccessResponse()


# def application_is_expired (dca) :
#     current_year = datetime.now().year
#     return dca.period_end < current_year


def send_dca_confirmation_email(dca):
    text_message = """
    Bonjour,

    Nous vous confirmons la réception de votre dossier de demande d'agrément au double-comptage.

    Bonne journée,
    L'équipe CarbuRe
    """
    email_subject = "Carbure - Dossier Double Comptage"
    cc = None
    if os.getenv("IMAGE_TAG", "dev") != "prod":
        # send only to staff / superuser
        recipients = ["carbure@beta.gouv.fr"]
    else:
        # PROD
        recipients = [
            r.user.email
            for r in UserRights.objects.filter(entity=dca.producer, user__is_staff=False, user__is_superuser=False).exclude(
                role__in=[UserRights.AUDITOR, UserRights.RO]
            )
        ]
        cc = "carbure@beta.gouv.fr"

    email = EmailMessage(
        subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc
    )
    email.send(fail_silently=False)
