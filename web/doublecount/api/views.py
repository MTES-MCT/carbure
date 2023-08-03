import datetime
import os
import traceback
import unicodedata
import boto3
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models.aggregates import Count, Sum

import xlsxwriter
from django.http import JsonResponse, HttpResponse
from admin.api.double_counting.applications.add import send_dca_confirmation_email
from core.decorators import check_rights, is_admin, is_admin_or_external_admin
import pytz
import traceback
import pandas as pd

from producers.models import ProductionSite
from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingDocFile,
    DoubleCountingSourcing,
    DoubleCountingProduction,
)
from doublecount.serializers import DoubleCountingApplicationPartialSerializer
from doublecount.serializers import (
    DoubleCountingApplicationPartialSerializerWithForeignKeys,
)
from core.models import Entity, UserRights, MatierePremiere, Pays, Biocarburant, CarbureLot
from core.xlsx_v3 import (
    export_dca,
    make_biofuels_sheet,
    make_dc_mps_sheet,
    make_countries_sheet,
    make_dc_production_sheet,
    make_dc_sourcing_sheet,
)
from carbure.storage_backends import AWSStorage
from django.core.files.storage import FileSystemStorage

from doublecount.old_helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data


@check_rights("entity_id")
def get_applications(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    applications = DoubleCountingApplication.objects.filter(producer=entity)
    serializer = DoubleCountingApplicationPartialSerializer(applications, many=True)
    return JsonResponse({"status": "success", "data": serializer.data})


# @is_admin_or_external_admin
# def get_applications_snapshot_admin(request):
#     years1 = [y["period_start__year"] for y in DoubleCountingApplication.objects.values("period_start__year").distinct()]
#     years2 = [y["period_end__year"] for y in DoubleCountingApplication.objects.values("period_end__year").distinct()]
#     years = list(set(years1 + years2))
#     data = {"years": years}
#     return JsonResponse({"status": "success", "data": data})


@check_rights("entity_id")
def get_application(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    application_id = request.GET.get("dca_id", None)
    export = request.GET.get("export", False)

    if not application_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        application = DoubleCountingApplication.objects.get(producer=entity, id=application_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find DCA application"}, status=400)
    serializer = DoubleCountingApplicationPartialSerializerWithForeignKeys(application)

    if not export:
        return JsonResponse({"status": "success", "data": serializer.data})
    else:
        file_location = export_dca(application)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
        return response


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def upload_file(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    production_site_id = request.POST.get("production_site_id", None)
    if not production_site_id:
        return JsonResponse({"status": "error", "message": "Missing production_site_id"}, status=400)

    f = request.FILES.get("file")
    if f is None:
        return JsonResponse({"status": "error", "message": "Missing File"}, status=400)

    if not ProductionSite.objects.filter(producer=entity, id=production_site_id).exists():
        return JsonResponse({"status": "error", "message": "Production site not found"}, status=400)

    # save file
    directory = "/tmp"
    now = datetime.datetime.now()
    filename = "%s_%s.xlsx" % (now.strftime("%Y%m%d.%H%M%S"), entity.name.upper())
    filename = "".join((c for c in unicodedata.normalize("NFD", filename) if unicodedata.category(c) != "Mn"))
    filepath = "%s/%s" % (directory, filename)
    with open(filepath, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    sourcing_data, production_data = load_dc_file(filepath)

    # get dc period for upload
    years = list(sourcing_data["year"]) + list(production_data["year"])
    end_year = max(years)
    start = datetime.date(end_year - 1, 1, 1)
    end = datetime.date(end_year, 12, 31)

    dca, created = DoubleCountingApplication.objects.get_or_create(
        producer=entity,
        production_site_id=production_site_id,
        period_start=start,
        period_end=end,
        defaults={"producer_user": request.user},
    )

    try:
        load_dc_sourcing_data(dca, sourcing_data)
        load_dc_production_data(dca, production_data)
        # send confirmation email
        try:
            send_dca_confirmation_email(dca)
        except:
            print("email send error")
            traceback.print_exc()
        return JsonResponse({"status": "success", "data": {"dca_id": dca.id}})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "File parsing error"}, status=400)


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def upload_documentation(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.POST.get("dca_id", None)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingApplication.objects.get(producer=entity, id=dca_id)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    file_obj = request.FILES.get("file")
    if file_obj is None:
        return JsonResponse({"status": "error", "message": "Missing File"}, status=400)

    # organize a path for the file in bucket
    file_directory_within_bucket = "{year}/{entity}".format(year=dca.period_start.year, entity=entity.name)
    filename = "".join((c for c in unicodedata.normalize("NFD", file_obj.name) if unicodedata.category(c) != "Mn"))

    # synthesize a full file path; note that we included the filename
    file_path_within_bucket = os.path.join(file_directory_within_bucket, filename)

    if "TEST" in os.environ and os.environ["TEST"] == "1":
        media_storage = FileSystemStorage("/tmp")
    else:
        media_storage = AWSStorage()
    media_storage.save(file_path_within_bucket, file_obj)
    file_url = media_storage.url(file_path_within_bucket)
    dcf = DoubleCountingDocFile()
    dcf.dca = dca
    dcf.url = file_url
    dcf.file_name = filename
    dcf.link_expiry_dt = pytz.utc.localize(datetime.datetime.now() + datetime.timedelta(seconds=3600))
    dcf.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id")
def download_documentation(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.GET.get("dca_id", None)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingApplication.objects.get(producer=entity, id=dca_id)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    file_id = request.GET.get("file_id", None)
    if not file_id:
        return JsonResponse({"status": "error", "message": "Missing file_id"}, status=400)
    try:
        f = DoubleCountingDocFile.objects.get(id=file_id, dca=dca, file_type=DoubleCountingDocFile.SOURCING)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    filepath = "/tmp/%s" % (f.file_name)
    s3filepath = "{year}/{entity}/{filename}".format(year=dca.period_start.year, entity=entity.name, filename=f.file_name)
    with open(filepath, "wb") as file:
        s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)
    with open(filepath, "rb") as file:
        data = file.read()
        ctype = "application/force-download"
        response = HttpResponse(content=data, content_type=ctype)
        response["Content-Disposition"] = 'attachment; filename="%s"' % (f.file_name)
    return response


@check_rights("entity_id")
def download_admin_decision(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.GET.get("dca_id", None)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingApplication.objects.get(producer=entity, id=dca_id)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    file_id = request.GET.get("file_id", None)
    if not file_id:
        return JsonResponse({"status": "error", "message": "Missing file_id"}, status=400)
    try:
        f = DoubleCountingDocFile.objects.get(id=file_id, dca=dca, file_type=DoubleCountingDocFile.DECISION)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    filepath = "/tmp/%s" % (f.file_name)
    s3filepath = "{year}/{entity}/{filename}".format(year=dca.period_start.year, entity=entity.name, filename=f.file_name)
    with open(filepath, "wb") as file:
        s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)
    with open(filepath, "rb") as file:
        data = file.read()
        ctype = "application/force-download"
        response = HttpResponse(content=data, content_type=ctype)
        response["Content-Disposition"] = 'attachment; filename="%s"' % (f.file_name)
    return response


@is_admin_or_external_admin
def admin_download_admin_decision(request):
    dca_id = request.GET.get("dca_id", None)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingApplication.objects.get(id=dca_id)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    file_id = request.GET.get("file_id", None)
    if not file_id:
        return JsonResponse({"status": "error", "message": "Missing file_id"}, status=400)
    try:
        f = DoubleCountingDocFile.objects.get(id=file_id, dca=dca, file_type=DoubleCountingDocFile.DECISION)
    except:
        return JsonResponse({"status": "forbidden", "message": "Forbidden"}, status=403)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_S3_REGION_NAME"],
        endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
        use_ssl=os.environ["AWS_S3_USE_SSL"],
    )
    filepath = "/tmp/%s" % (f.file_name)
    s3filepath = "{year}/{entity}/{filename}".format(
        year=dca.period_start.year, entity=dca.producer.name, filename=f.file_name
    )
    with open(filepath, "wb") as file:
        s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)
    with open(filepath, "rb") as file:
        data = file.read()
        ctype = "application/force-download"
        response = HttpResponse(content=data, content_type=ctype)
        response["Content-Disposition"] = 'attachment; filename="%s"' % (f.file_name)
    return response


def get_template(request):
    location = "/tmp/carbure_template_DC.xlsx"
    workbook = xlsxwriter.Workbook(location)
    make_dc_sourcing_sheet(workbook)
    make_dc_production_sheet(workbook)
    make_dc_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    workbook.close()
    with open(location, "rb") as f:
        file_data = f.read()
        response = HttpResponse(file_data, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = 'attachment; filename="carbure_template_DC.xlsx"'
        return response


@is_admin
def get_quotas_snapshot_admin(request, *args, **kwargs):
    # bon courage
    year = request.GET.get("year", False)  # mandatory
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)
    producers = {p.id: p for p in Entity.objects.filter(entity_type=Entity.PRODUCER)}
    production_sites = {p.id: p for p in ProductionSite.objects.all()}
    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    # get a detailed list of production quotas per production site
    # ex: 2021 - PRODUCER TEST - PRODUCTION SITE 01 - BIOFUELID - FEEDSTOCKID - METRICTONNES
    detailed_quotas = DoubleCountingProduction.objects.values(
        "year", "dca__producer", "dca__production_site", "biofuel", "feedstock", "approved_quota"
    ).filter(year=year, feedstock_id__in=feedstocks.keys())
    # get a sum of all double count production
    # 2021 - PRODUCER TEST - PRODUCTION SITE 01 - BIOFUELID - FEEDSTOCKID - VOLUME
    double_counted_production = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_producer__in=producers.keys(),
            carbure_production_site__in=production_sites.keys(),
            year=year,
            feedstock_id__in=feedstocks.keys(),
            biofuel_id__in=biofuels.keys(),
        )
        .values("year", "carbure_producer", "carbure_production_site", "feedstock", "biofuel", "biofuel__masse_volumique")
        .annotate(volume=Sum("volume"))
    )

    # Merge both datasets
    df1 = pd.DataFrame(detailed_quotas).rename(
        columns={
            "dca__producer": "producer_id",
            "dca__production_site": "production_site_id",
            "biofuel": "biofuel_id",
            "feedstock": "feedstock_id",
        }
    )
    df2 = pd.DataFrame(double_counted_production).rename(
        columns={
            "carbure_producer": "producer_id",
            "carbure_production_site": "production_site_id",
            "feedstock": "feedstock_id",
            "biofuel": "biofuel_id",
            "biofuel__masse_volumique": "masse_volumique",
        }
    )
    df1.set_index(["year", "producer_id", "production_site_id", "biofuel_id", "feedstock_id"], inplace=True)
    df2.set_index(["year", "producer_id", "production_site_id", "biofuel_id", "feedstock_id"], inplace=True)
    res = df1.merge(df2, how="outer", left_index=True, right_index=True).fillna(0)
    res["current_production_weight_sum_tonnes"] = (res["volume"] * res["masse_volumique"] / 1000).apply(
        lambda x: round(x, 2)
    )
    res["full"] = (res["current_production_weight_sum_tonnes"] == res["approved_quota"]).astype(int)
    res["breached"] = (res["current_production_weight_sum_tonnes"] > res["approved_quota"]).astype(int)
    grouped = res.groupby(["year", "producer_id", "production_site_id"]).agg(
        nb_quotas=("full", "count"),
        nb_full_quotas=("full", "sum"),
        nb_breached_quotas=("breached", "sum"),
        approved_quota_weight_sum=("approved_quota", "sum"),
        current_production_weight_sum=("volume", "sum"),
    )
    grouped.reset_index(inplace=True)
    grouped["producer"] = grouped["producer_id"].apply(lambda x: producers[x].natural_key())
    grouped["production_site"] = grouped["production_site_id"].apply(lambda x: production_sites[x].natural_key())
    return JsonResponse({"status": "success", "data": grouped.to_dict("records")})


@is_admin
def upload_decision_admin(request):
    dca_id = request.POST.get("dca_id", None)
    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingApplication.objects.get(id=dca_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find DCA"}, status=400)

    file_obj = request.FILES.get("file")
    if file_obj is None:
        return JsonResponse({"status": "error", "message": "Missing File"}, status=400)

    # organize a path for the file in bucket
    file_directory_within_bucket = "{year}/{entity}".format(year=dca.period_start.year, entity=dca.producer.name)
    filename = "".join((c for c in unicodedata.normalize("NFD", file_obj.name) if unicodedata.category(c) != "Mn"))

    # synthesize a full file path; note that we included the filename
    file_path_within_bucket = os.path.join(file_directory_within_bucket, filename)

    if "TEST" in os.environ and os.environ["TEST"] == "1":
        media_storage = FileSystemStorage("/tmp")
    else:
        media_storage = AWSStorage()
    media_storage.save(file_path_within_bucket, file_obj)
    file_url = media_storage.url(file_path_within_bucket)
    dcf = DoubleCountingDocFile()
    dcf.dca = dca
    dcf.url = file_url
    dcf.file_name = filename
    dcf.file_type = DoubleCountingDocFile.DECISION
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
    f = open(filepath, "rb")
    # send an email
    recipients = [u.user.email for u in UserRights.objects.filter(entity=dca.producer, role=UserRights.ADMIN)]
    subject = "CarbuRe - Agrément Double Compte"
    body = """
    Bonjour,

    La décision d'agrément au double comptage concernant votre site de production %s est désormais accessible sur votre compte CarbuRe.
    Vous en trouverez une copie ci-joint.

    Merci
    """ % (
        dca.production_site.name
    )
    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        ["carbure@beta.gouv.fr"],
    )
    email.attach(filename, f.read())
    email.send()
    f.close()
    return JsonResponse({"status": "success"})


@is_admin_or_external_admin
def get_production_site_quotas_admin(request, *args, **kwargs):
    year = request.GET.get("year", False)  # mandatory
    production_site_id = request.GET.get("production_site_id", False)
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)

    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    detailed_quotas = DoubleCountingProduction.objects.values("biofuel", "feedstock", "approved_quota").filter(
        year=year, dca__production_site_id=production_site_id
    )
    production = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], carbure_production_site_id=production_site_id, year=year
        )
        .values("feedstock", "biofuel", "biofuel__masse_volumique")
        .filter(feedstock_id__in=feedstocks.keys())
        .annotate(volume=Sum("volume"), nb_lots=Count("id"))
    )

    # Merge both datasets
    df1 = pd.DataFrame(columns={"biofuel", "feedstock", "approved_quota"}, data=detailed_quotas).rename(
        columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"}
    )
    df2 = pd.DataFrame(
        columns={"feedstock", "biofuel", "volume", "nb_lots", "biofuel__masse_volumique"}, data=production
    ).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id", "biofuel__masse_volumique": "masse_volumique"})
    df1.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    df2.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    res = df1.merge(df2, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
    res["feedstock"] = res["feedstock_id"].apply(lambda x: feedstocks[x].natural_key())
    res["biofuel"] = res["biofuel_id"].apply(lambda x: biofuels[x].natural_key())
    res["current_production_weight_sum_tonnes"] = (res["volume"] * res["masse_volumique"] / 1000).apply(
        lambda x: round(x, 2)
    )
    return JsonResponse({"status": "success", "data": res.to_dict("records")})


@check_rights("entity_id")
def get_production_site_quotas(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.GET.get("dca_id", False)
    biofuels = {p.id: p for p in Biocarburant.objects.all()}
    feedstocks = {m.id: m for m in MatierePremiere.objects.filter(is_double_compte=True)}

    try:
        dca = DoubleCountingApplication.objects.get(id=dca_id, producer=entity)
    except:
        return JsonResponse({"status": "error", "message": "Not authorised"}, status=403)

    detailed_quotas = DoubleCountingProduction.objects.values("biofuel", "feedstock", "approved_quota").filter(dca_id=dca_id)
    production = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], carbure_production_site_id=dca.production_site
        )
        .values("year", "feedstock", "biofuel", "biofuel__masse_volumique")
        .filter(feedstock_id__in=feedstocks.keys())
        .annotate(volume=Sum("volume"), nb_lots=Count("id"))
    )

    # Merge both datasets
    df1 = pd.DataFrame(columns={"biofuel", "feedstock", "approved_quota"}, data=detailed_quotas).rename(
        columns={"biofuel": "biofuel_id", "feedstock": "feedstock_id"}
    )
    df2 = pd.DataFrame(
        columns={"feedstock", "biofuel", "volume", "nb_lots", "biofuel__masse_volumique"}, data=production
    ).rename(columns={"feedstock": "feedstock_id", "biofuel": "biofuel_id", "biofuel__masse_volumique": "masse_volumique"})
    df1.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    df2.set_index(["biofuel_id", "feedstock_id"], inplace=True)
    res = df1.merge(df2, how="outer", left_index=True, right_index=True).fillna(0).reset_index()
    res["feedstock"] = res["feedstock_id"].apply(lambda x: feedstocks[x].natural_key())
    res["biofuel"] = res["biofuel_id"].apply(lambda x: biofuels[x].natural_key())
    res["current_production_weight_sum_tonnes"] = (res["volume"] * res["masse_volumique"] / 1000).apply(
        lambda x: round(x, 2)
    )
    return JsonResponse({"status": "success", "data": res.to_dict("records")})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def remove_sourcing(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_sourcing_id = request.POST.get("dca_sourcing_id", False)

    if not dca_sourcing_id:
        return JsonResponse({"status": "error", "message": "Missing dca_sourcing_id"}, status=400)

    try:
        to_delete = DoubleCountingSourcing.objects.get(dca__producer=entity, id=dca_sourcing_id)
        if to_delete.dca.status == DoubleCountingApplication.PENDING:
            to_delete.delete()
        else:
            return JsonResponse({"status": "forbidden", "message": "Application cannot be updated"}, status=403)
    except:
        return JsonResponse({"status": "error", "message": "Could not find Sourcing Line"}, status=400)
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def remove_production(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_production_id = request.POST.get("dca_production_id", False)

    if not dca_production_id:
        return JsonResponse({"status": "error", "message": "Missing dca_production_id"}, status=400)

    try:
        to_delete = DoubleCountingProduction.objects.get(dca__producer=entity, id=dca_production_id)
        if to_delete.dca.status == DoubleCountingApplication.PENDING:
            to_delete.delete()
        else:
            return JsonResponse({"status": "forbidden", "message": "Application cannot be updated"}, status=403)
    except:
        return JsonResponse({"status": "error", "message": "Could not find Production Line"}, status=400)
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def add_sourcing(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.POST.get("dca_id", False)
    year = request.POST.get("year", False)
    metric_tonnes = request.POST.get("metric_tonnes", False)
    feedstock_code = request.POST.get("feedstock_code", False)
    origin_country_code = request.POST.get("origin_country_code", False)
    supply_country_code = request.POST.get("supply_country_code", False)
    transit_country_code = request.POST.get("transit_country_code", False)

    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    if not year:
        return JsonResponse({"status": "error", "message": "Missing year"}, status=400)
    if not metric_tonnes:
        return JsonResponse({"status": "error", "message": "Missing metric_tonnes"}, status=400)
    if not feedstock_code:
        return JsonResponse({"status": "error", "message": "Missing feedstock_code"}, status=400)
    if not origin_country_code:
        return JsonResponse({"status": "error", "message": "Missing origin_country_code"}, status=400)
    if not supply_country_code:
        return JsonResponse({"status": "error", "message": "Missing supply_country_code"}, status=400)
    if not transit_country_code:
        return JsonResponse({"status": "error", "message": "Missing transit_country_code"}, status=400)

    try:
        dca = DoubleCountingApplication.objects.get(producer=entity, id=dca_id, status=DoubleCountingApplication.PENDING)
    except:
        return JsonResponse({"status": "forbidden", "message": "Could not find DCA"}, status=403)

    if dca.status != DoubleCountingApplication.PENDING:
        return JsonResponse({"status": "forbidden", "message": "application cannot be updated"}, status=403)

    dcs = DoubleCountingSourcing()
    dcs.dca = dca
    dcs.year = year
    try:
        feedstock = MatierePremiere.objects.get(code=feedstock_code)
        dcs.feedstock = feedstock
    except:
        return JsonResponse({"status": "error", "message": "Could not find feedstock"}, status=400)

    try:
        oc = Pays.objects.get(code_pays=origin_country_code)
        dcs.origin_country = oc
    except:
        return JsonResponse({"status": "error", "message": "Could not find origin_country"}, status=400)
    try:
        sc = Pays.objects.get(code_pays=supply_country_code)
        dcs.supply_country = sc
    except:
        return JsonResponse({"status": "error", "message": "Could not find supply_country"}, status=400)
    try:
        tc = Pays.objects.get(code_pays=transit_country_code)
        dcs.transit_country = tc
    except:
        return JsonResponse({"status": "error", "message": "Could not find transit_country"}, status=400)
    dcs.metric_tonnes = metric_tonnes
    try:
        dcs.save()
    except:
        return JsonResponse({"status": "error", "message": "Could not save sourcing line"}, status=400)
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def add_production(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_id = request.POST.get("dca_id", False)
    year = request.POST.get("year", False)
    feedstock_code = request.POST.get("feedstock_code", False)
    biofuel_code = request.POST.get("biofuel_code", False)
    max_production_capacity = request.POST.get("max_production_capacity", False)
    estimated_production = request.POST.get("estimated_production", False)
    requested_quota = request.POST.get("requested_quota", False)

    if not dca_id:
        return JsonResponse({"status": "error", "message": "Missing dca_id"}, status=400)
    if not feedstock_code:
        return JsonResponse({"status": "error", "message": "Missing feedstock_code"}, status=400)
    if not biofuel_code:
        return JsonResponse({"status": "error", "message": "Missing biofuel_code"}, status=400)
    if not max_production_capacity:
        return JsonResponse({"status": "error", "message": "Missing max_production_capacity"}, status=400)
    if not estimated_production:
        return JsonResponse({"status": "error", "message": "Missing estimated_production"}, status=400)
    if not requested_quota:
        return JsonResponse({"status": "error", "message": "Missing requested_quota"}, status=400)

    try:
        dca = DoubleCountingApplication.objects.get(producer=entity, id=dca_id, status=DoubleCountingApplication.PENDING)
    except:
        return JsonResponse({"status": "forbidden", "message": "Could not find DCA"}, status=403)

    if dca.status != DoubleCountingApplication.PENDING:
        return JsonResponse({"status": "forbidden", "message": "application cannot be updated"}, status=403)

    dcp = DoubleCountingProduction()
    dcp.dca = dca
    dcp.year = year
    try:
        feedstock = MatierePremiere.objects.get(code=feedstock_code)
        dcp.feedstock = feedstock
    except:
        return JsonResponse({"status": "error", "message": "Could not find feedstock"}, status=400)
    try:
        biofuel = Biocarburant.objects.get(code=biofuel_code)
        dcp.biofuel = biofuel
    except:
        return JsonResponse({"status": "error", "message": "Could not find biofuel"}, status=400)

    dcp.max_production_capacity = max_production_capacity
    dcp.estimated_production = estimated_production
    dcp.requested_quota = requested_quota
    try:
        dcp.save()
    except:
        return JsonResponse({"status": "error", "message": "Could not save production line"}, status=400)
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def update_sourcing(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_sourcing_id = request.POST.get("dca_sourcing_id", False)
    metric_tonnes = request.POST.get("metric_tonnes", False)

    if not dca_sourcing_id:
        return JsonResponse({"status": "error", "message": "Missing dca_sourcing_id"}, status=400)
    if not metric_tonnes:
        return JsonResponse({"status": "error", "message": "Missing metric_tonnes"}, status=400)

    try:
        to_update = DoubleCountingSourcing.objects.get(dca__producer=entity, id=dca_sourcing_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find Sourcing Line"}, status=400)
    if to_update.dca.status != DoubleCountingApplication.PENDING:
        return JsonResponse({"status": "forbidden", "message": "application cannot be updated"}, status=403)

    to_update.metric_tonnes = metric_tonnes
    try:
        to_update.save()
    except:
        return JsonResponse({"status": "error", "message": "Could not update Sourcing line"}, status=400)
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def update_production(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    dca_production_id = request.POST.get("dca_production_id", False)
    max_production_capacity = request.POST.get("max_production_capacity", False)
    estimated_production = request.POST.get("estimated_production", False)
    requested_quota = request.POST.get("requested_quota", False)

    if not dca_production_id:
        return JsonResponse({"status": "error", "message": "Missing dca_production_id"}, status=400)

    try:
        to_update = DoubleCountingProduction.objects.get(dca__producer=entity, id=dca_production_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find Production Line"}, status=400)
    if to_update.dca.status != DoubleCountingApplication.PENDING:
        return JsonResponse({"status": "forbidden", "message": "application cannot be updated"}, status=403)
    if max_production_capacity:
        to_update.max_production_capacity = max_production_capacity
    if estimated_production:
        to_update.estimated_production = estimated_production
    if requested_quota:
        to_update.requested_quota = requested_quota
    try:
        to_update.save()
    except:
        return JsonResponse({"status": "error", "message": "Could not update Production line"}, status=400)
    return JsonResponse({"status": "success"})
