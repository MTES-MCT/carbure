import datetime
from django.core.mail import EmailMessage
from django.db.models import Q

import traceback
import os

import pytz
from carbure import settings
import unicodedata
import boto3
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


class DoubleCountingAddError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PRODUCER_NOT_FOUND = "PRODUCER_NOT_FOUND"
    PRODUCTION_SITE_NOT_FOUND = "PRODUCTION_SITE_NOT_FOUND"
    PRODUCTION_SITE_ADDRESS_UNDEFINED = "PRODUCTION_SITE_ADDRESS_UNDEFINED"
    APPLICATION_ALREADY_RECEIVED = "APPLICATION_ALREADY_RECEIVED"
    APPLICATION_ALREADY_EXISTS = "APPLICATION_ALREADY_EXISTS"
    MISSING_FILE = "MISSING_FILE"


@check_admin_rights()
@transaction.atomic
def add_application(request, *args, **kwargs):
    producer_id = request.POST.get("producer_id", None)
    should_replace = request.POST.get("should_replace") == "true"
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

    identical_replacable_application = DoubleCountingApplication.objects.filter(
        Q(producer=producer)
        & Q(period_start__year=start.year)
        & Q(status__in=[DoubleCountingApplication.PENDING, DoubleCountingApplication.REJECTED]),
    )

    if identical_replacable_application.exists():
        if should_replace:
            identical_replacable_application.delete()
        else:
            return ErrorResponse(400, DoubleCountingAddError.APPLICATION_ALREADY_EXISTS)

    dca, created = DoubleCountingApplication.objects.get_or_create(
        producer=producer,
        production_site_id=production_site_id,
        period_start=start,
        period_end=end,
        defaults={"producer_user": request.user},
    )

    if not created:
        return ErrorResponse(400, DoubleCountingAddError.APPLICATION_ALREADY_RECEIVED)

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
        upload_file(dca, file)
    except:
        print("upload error")
        traceback.print_exc()

    try:
        send_dca_confirmation_email(dca)
    except:
        print("email send error")
        traceback.print_exc()
    return SuccessResponse()


# def application_is_expired (dca) :
#     current_year = datetime.now().year
#     return dca.period_end < current_year


def upload_file(dca, file):
    # organize a path for the file in bucket
    file_directory_within_bucket = "{year}/{entity}".format(year=dca.period_start.year, entity=dca.producer.name)
    filename = "".join((c for c in unicodedata.normalize("NFD", file.name) if unicodedata.category(c) != "Mn"))

    # synthesize a full file path; note that we included the filename
    file_path_within_bucket = os.path.join(file_directory_within_bucket, filename)

    if "TEST" in os.environ and os.environ["TEST"] == "1":
        media_storage = FileSystemStorage("/tmp")
    else:
        media_storage = AWSStorage()
    media_storage.save(file_path_within_bucket, file)
    file_url = media_storage.url(file_path_within_bucket)
    dcf = DoubleCountingDocFile()
    dcf.dca = dca
    dcf.agreement_id = dca.agreement_id
    dcf.url = file_url
    dcf.file_name = filename
    dcf.file_type = DoubleCountingDocFile.SOURCING
    dcf.link_expiry_dt = pytz.utc.localize(datetime.datetime.now() + datetime.timedelta(seconds=3600))
    dcf.save()

    # get the file
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    s3filepath = "{year}/{entity}/{filename}".format(
        year=dca.period_start.year, entity=dca.producer.name, filename=dcf.file_name
    )
    filepath = "/tmp/%s" % (dcf.file_name)
    with open(filepath, "wb") as file:
        s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)


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
            for r in UserRights.objects.filter(
                entity=dca.producer, user__is_staff=False, user__is_superuser=False, status=UserRights.ACCEPTED
            ).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])
        ]
        cc = "carbure@beta.gouv.fr"

    email = EmailMessage(
        subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc
    )
    email.send(fail_silently=False)
