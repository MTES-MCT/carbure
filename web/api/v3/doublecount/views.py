import datetime
from email import message
import os
import traceback
import unicodedata
import boto3
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import json
from django.db.models.aggregates import Count, Sum
from django.db.models.query_utils import Q

import xlsxwriter
from django.http import JsonResponse, HttpResponse
from core.decorators import check_rights, is_admin, is_admin_or_external_admin
import pytz
import traceback

from producers.models import ProductionSite
from doublecount.models import DoubleCountingAgreement, DoubleCountingDocFile, DoubleCountingSourcing, DoubleCountingProduction
from doublecount.serializers import DoubleCountingAgreementFullSerializer, DoubleCountingAgreementPartialSerializer
from doublecount.serializers import DoubleCountingAgreementFullSerializerWithForeignKeys, DoubleCountingAgreementPartialSerializerWithForeignKeys
from doublecount.helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data
from core.models import Entity, LotTransaction, LotV2, UserRights, MatierePremiere, Pays, Biocarburant
from core.xlsx_v3 import export_dca, make_biofuels_sheet, make_dc_mps_sheet, make_countries_sheet, make_dc_production_sheet, make_dc_sourcing_sheet
from carbure.storage_backends import AWSStorage
from django.core.files.storage import FileSystemStorage

@check_rights('entity_id')
def get_agreements(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    agreements = DoubleCountingAgreement.objects.filter(producer=entity)
    serializer = DoubleCountingAgreementPartialSerializer(agreements, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})


@is_admin_or_external_admin
def get_agreements_admin(request):
    year = request.GET.get('year', False)
    if not year:
        return JsonResponse({'status': 'error', 'message': 'Missing year'}, status=400)

    agreements = DoubleCountingAgreement.objects.filter(Q(period_start__year=year) | Q(period_end__year=year))
    accepted = agreements.filter(status=DoubleCountingAgreement.ACCEPTED)
    accepted_count = accepted.count()
    rejected = agreements.filter(status=DoubleCountingAgreement.REJECTED)
    rejected_count = rejected.count()
    expired = agreements.filter(status=DoubleCountingAgreement.LAPSED)
    expired_count = expired.count()
    pending = agreements.filter(status=DoubleCountingAgreement.PENDING)
    pending_count = pending.count()
    progress = agreements.filter(status=DoubleCountingAgreement.INPROGRESS)
    progress_count = progress.count()


    accepted_s = DoubleCountingAgreementFullSerializer(accepted, many=True)
    rejected_s = DoubleCountingAgreementFullSerializer(rejected, many=True)
    expired_s = DoubleCountingAgreementFullSerializer(expired, many=True)
    pending_s = DoubleCountingAgreementFullSerializer(pending, many=True)
    progress_s = DoubleCountingAgreementFullSerializer(progress, many=True)
    data = {'accepted': {'count': accepted_count, 'agreements': accepted_s.data}, 
            'rejected':  {'count': rejected_count, 'agreements': rejected_s.data}, 
            'expired': {'count': expired_count, 'agreements': expired_s.data},  
            'progress': {'count': progress_count, 'agreements': progress_s.data},
            'pending': {'count': pending_count, 'agreements': pending_s.data}, 
            }
    return JsonResponse({'status': 'success', 'data': data})

@is_admin_or_external_admin
def get_agreements_snapshot_admin(request):
    years1 = [y['period_start__year'] for y in DoubleCountingAgreement.objects.values('period_start__year').distinct()]
    years2 = [y['period_end__year'] for y in DoubleCountingAgreement.objects.values('period_end__year').distinct()]
    years = list(set(years1 + years2))
    data = {'years': years}
    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_agreement(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    agreement_id = request.GET.get('dca_id', None)
    export = request.GET.get('export', False)

    if not agreement_id:
        return JsonResponse({'status': 'error', 'message': 'Missing dca_id'}, status=400)
    try:
        agreement = DoubleCountingAgreement.objects.get(producer=entity, id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementPartialSerializerWithForeignKeys(agreement)

    if not export:
        return JsonResponse({'status': 'success', 'data': serializer.data})
    else:
        file_location = export_dca(agreement)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


@is_admin
def get_agreement_admin(request, *args, **kwargs):
    agreement_id = request.GET.get('dca_id', None)
    export = request.GET.get('export', False)

    if not agreement_id:
        return JsonResponse({'status': 'error', 'message': 'Missing dca_id'}, status=400)
    try:
        agreement = DoubleCountingAgreement.objects.get(id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementFullSerializerWithForeignKeys(agreement)
    if not export:
        return JsonResponse({'status': 'success', 'data': serializer.data})
    else:
        file_location = export_dca(agreement)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response

def send_dca_confirmation_email(dca):
    text_message = """ 
    Bonjour,

    Nous vous confirmons la réception de votre dossier de demande d'agrément au double-comptage.

    Bonne journée,
    L'équipe CarbuRe
    """
    email_subject = 'Carbure - Dossier Double Comptage'
    cc = None
    if os.getenv('IMAGE_TAG', 'dev') != 'prod':
        # send only to staff / superuser
        recipients = ['carbure@beta.gouv.fr']
    else:
        # PROD
        recipients = [r.user.email for r in UserRights.objects.filter(entity=dca.producer, user__is_staff=False, user__is_superuser=False).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])]
        cc = "carbure@beta.gouv.fr" 

    email = EmailMessage(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
    email.send(fail_silently=False)

def send_dca_status_email(dca):
    if dca.status == DoubleCountingAgreement.ACCEPTED:
        text_message = """ 
        Bonjour,

        Votre dossier de demande d'agrément au double-comptage pour le site de production %s a été accepté.

        Bonne journée,
        L'équipe CarbuRe
        """ % (dca.production_site.name)
    elif dca.status == DoubleCountingAgreement.REJECTED:
        text_message = """ 
        Bonjour,

        Votre dossier de demande d'agrément au double-comptage pour le site de production %s a été accepté.

        Bonne journée,
        L'équipe CarbuRe
        """  % (dca.production_site.name)
    else:
        # no mail to send
        return
    email_subject = 'Carbure - Dossier Double Comptage'
    cc = None
    if os.getenv('IMAGE_TAG', 'dev') != 'prod':
        # send only to staff / superuser
        recipients = ['carbure@beta.gouv.fr']
    else:
        # PROD
        recipients = [r.user.email for r in UserRights.objects.filter(entity=dca.producer, user__is_staff=False, user__is_superuser=False).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])]
        cc = "carbure@beta.gouv.fr" 
    email = EmailMessage(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
    email.send(fail_silently=False)


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def upload_file(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    production_site_id = request.POST.get('production_site_id', None)
    if not production_site_id:
        return JsonResponse({'status': "error", 'message': "Missing production_site_id"}, status=400)

    f = request.FILES.get('file')
    if f is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    if not ProductionSite.objects.filter(producer=entity, id=production_site_id).exists():
        return JsonResponse({'status': "error", 'message': "Production site not found"}, status=400)

    # save file
    directory = '/tmp'
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d.%H%M%S'), entity.name.upper())
    filename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
    filepath = '%s/%s' % (directory, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    sourcing_data, production_data = load_dc_file(filepath)

    # get dc period for upload
    years = list(sourcing_data['year']) + list(production_data['year'])
    end_year = max(years)
    start = datetime.date(end_year - 1, 1, 1)
    end = datetime.date(end_year, 12, 31)

    dca, created = DoubleCountingAgreement.objects.get_or_create(producer=entity, production_site_id=production_site_id, period_start=start, period_end=end, defaults={'producer_user': request.user})

    try:
        load_dc_sourcing_data(dca, sourcing_data)
        load_dc_production_data(dca, production_data)
        # send confirmation email
        try:
            send_dca_confirmation_email(dca)
        except:
            print('email send error')
            traceback.print_exc()
        return JsonResponse({'status': 'success', 'data': {'dca_id': dca.id}})
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "File parsing error"}, status=400)


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def upload_documentation(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.POST.get('dca_id', None)
    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Forbidden"}, status=403)

    file_obj = request.FILES.get('file')
    if file_obj is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # organize a path for the file in bucket
    file_directory_within_bucket = '{year}/{entity}'.format(year=dca.period_start.year, entity=entity.name)
    filename = ''.join((c for c in unicodedata.normalize('NFD', file_obj.name) if unicodedata.category(c) != 'Mn'))

    # synthesize a full file path; note that we included the filename
    file_path_within_bucket = os.path.join(
        file_directory_within_bucket,
        filename
    )

    if 'TEST' in os.environ and os.environ['TEST'] == '1':
        media_storage = FileSystemStorage('/tmp')
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
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def download_documentation(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.GET.get('dca_id', None)
    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Forbidden"}, status=403)

    file_id = request.GET.get('file_id', None)
    if not file_id:
        return JsonResponse({'status': "error", 'message': "Missing file_id"}, status=400)
    try:
        f = DoubleCountingDocFile.objects.get(id=file_id, dca=dca)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Forbidden"}, status=403)

    s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name=os.environ['AWS_S3_REGION_NAME'], endpoint_url=os.environ['AWS_S3_ENDPOINT_URL'], use_ssl=os.environ['AWS_S3_USE_SSL'])
    filepath = '/tmp/%s' % (f.file_name)
    s3filepath = '{year}/{entity}/{filename}'.format(year=dca.period_start.year, entity=entity.name, filename=f.file_name)
    with open(filepath, 'wb') as file:
        s3.download_fileobj(os.environ['AWS_DCDOCS_STORAGE_BUCKET_NAME'], s3filepath, file)
    with open(filepath, "rb") as file:
        data = file.read()
        ctype = "application/force-download"
        response = HttpResponse(content=data, content_type=ctype)
        response['Content-Disposition'] = 'attachment; filename="%s"' % (f.file_name)
    return response

@is_admin_or_external_admin
def admin_download_documentation(request, *args, **kwargs):
    dca_id = request.GET.get('dca_id', None)
    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)
    try:
        dca = DoubleCountingAgreement.objects.get(id=dca_id)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Forbidden"}, status=403)

    file_id = request.GET.get('file_id', None)
    if not file_id:
        return JsonResponse({'status': "error", 'message': "Missing file_id"}, status=400)
    try:
        f = DoubleCountingDocFile.objects.get(id=file_id, dca=dca)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Forbidden"}, status=403)
    s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'], region_name=os.environ['AWS_S3_REGION_NAME'], endpoint_url=os.environ['AWS_S3_ENDPOINT_URL'], use_ssl=os.environ['AWS_S3_USE_SSL'])
    filepath = '/tmp/%s' % (f.file_name)
    s3filepath = '{year}/{entity}/{filename}'.format(year=dca.period_start.year, entity=dca.producer.name, filename=f.file_name)
    with open(filepath, 'wb') as file:
        s3.download_fileobj(os.environ['AWS_DCDOCS_STORAGE_BUCKET_NAME'], s3filepath, file)
    with open(filepath, "rb") as file:
        data = file.read()
        ctype = "application/force-download"
        response = HttpResponse(content=data, content_type=ctype)
        response['Content-Disposition'] = 'attachment; filename="%s"' % (f.file_name)
    return response

def get_template(request):
    location = '/tmp/carbure_template_DC.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_dc_sourcing_sheet(workbook)
    make_dc_production_sheet(workbook)
    make_dc_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    workbook.close()
    with open(location, 'rb') as f:
        file_data = f.read()
        response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="carbure_template_DC.xlsx"'
        return response


@is_admin
def get_quotas_snapshot_admin(request, *args, **kwargs):
    year = request.GET.get('year', False) # mandatory
    producer_id = request.GET.get('producer_id', False)
    if not year:
        return JsonResponse({'status': "error", 'message': "Missing year"}, status=400)

    producers = {p.id: p for p in Entity.objects.filter(entity_type=Entity.PRODUCER)}
    production_sites = {p.id: p for p in ProductionSite.objects.all()}

    quotas = DoubleCountingProduction.objects.values('year', 'dca__producer', 'dca__production_site').filter(year=year)
    if producer_id:
        quotas = quotas.filter(dca__producer_id=producer_id)
    quotas = quotas.annotate(approved_quota_weight_sum=Sum('approved_quota'), nb_quotas=Count('approved_quota'))


    detailed_quotas = DoubleCountingProduction.objects.values('year', 'dca__producer', 'dca__production_site', 'biofuel', 'feedstock', 'approved_quota').filter(year=year)
    if producer_id:
        detailed_quotas = detailed_quotas.filter(dca__producer_id=producer_id)
    detailed_quotas = {'%d.%d.%d.%d' % (dq['dca__producer'], dq['dca__production_site'], dq['biofuel'], dq['feedstock']): dq for dq in detailed_quotas}
    # print(quotas)
    # [{'year': 2021, 'dca__producer': 10, 'dca__production_site': 2, 'approved_quota_weight_sum': 2000, 'nb_quotas': 2}, {'year': 2021, 'dca__producer': 13, 'dca__production_site': 8, 'sum': 1000, 'nb_quotas': 1}]

    # detailed
    all_lines = DoubleCountingProduction.objects.values('year', 'dca__producer', 'dca__production_site', 'biofuel', 'feedstock').filter(year=year)
    producers_ids = producers.keys()
    prodsites_ids = production_sites.keys()
    feedstocks_ids = [m.id for m in MatierePremiere.objects.filter(is_double_compte=True)]
    biofuels_ids = list(set([q['biofuel'] for q in all_lines]))
    consumed_quotas = LotTransaction.objects.filter(lot__status=LotV2.VALIDATED, lot__carbure_producer__in=producers_ids, lot__carbure_production_site__in=prodsites_ids, lot__year=year, lot__matiere_premiere_id__in=feedstocks_ids, lot__biocarburant_id__in=biofuels_ids) \
        .values('lot__year', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__matiere_premiere', 'lot__biocarburant').annotate(volume=Sum('lot__volume'))
    # print(consumed_quotas)
    # {'lot__year': 2021, 'lot__carbure_producer': 10, 'lot__carbure_production_site': 2, 'lot__matiere_premiere': 69, 'lot__biocarburant': 33, 'volume': 109371.0}
    data = {}
    for q in quotas:
        key = "%d.%d" % (q['dca__producer'], q['dca__production_site'])
        d = {'producer': producers[q['dca__producer']].natural_key(), 
             'production_site': production_sites[q['dca__production_site']].natural_key(), 
             'current_production_weight_sum': 0, 'approved_quota_weight_sum': q['approved_quota_weight_sum'],
             'nb_quotas': q['nb_quotas'], 'nb_full_quotas': 0, 'nb_breached_quotas': 0}
        data[key] = d
    for c in consumed_quotas:
        key = '%d.%d.%d.%d' % (c['lot__carbure_producer'], c['lot__carbure_production_site'], c['lot__biocarburant'], c['lot__matiere_premiere'])
        smallkey = '%d.%d' % (c['lot__carbure_producer'], c['lot__carbure_production_site'])
        if key in detailed_quotas:
            dq = detailed_quotas[key]
            data[smallkey]['current_production_weight_sum'] += c['volume']
            if c['volume'] > dq['approved_quota']:
                data[smallkey]['nb_breached_quotas'] += 1
            elif c['volume'] == dq['approved_quota']:
                data[smallkey]['nb_full_quotas'] += 1
            else:
                pass
        else:
            # lot sent with no approved quota!!!
            if smallkey not in data:
                data[smallkey] = {'producer': producers[c['lot__carbure_producer']].natural_key(),
                                  'production_site': production_sites[c['lot__carbure_production_site']].natural_key(), 
                                  'current_production_weight_sum': 0, 'approved_quota_weight_sum': 0,
                                  'nb_quotas':0, 'nb_full_quotas': 0, 'nb_breached_quotas': 0}
            data[smallkey]['nb_breached_quotas'] += 1
            data[smallkey]['nb_full_quotas'] += 1
    tosend = [v for k, v in data.items()]
    return JsonResponse({'status': "success", 'data': tosend})


@is_admin_or_external_admin
def get_quotas_admin(request, *args, **kwargs):
    year = request.GET.get('year', False) # mandatory
    producer_id = request.GET.get('producer_id', False)
    production_site_id = request.GET.get('production_site_id', False)
    feedstock_id = request.GET.get('feedstock_id', False)
    biofuel_id = request.GET.get('biofuel_id', False)
    if not year:
        return JsonResponse({'status': "error", 'message': "Missing year"}, status=400)

    quotas = DoubleCountingProduction.objects.values('year', 'dca__producer', 'dca__production_site', 'biofuel', 'feedstock', 'approved_quota').filter(year=year)
    if producer_id:
        quotas = quotas.filter(dca__producer_id=producer_id)
    if production_site_id:
        quotas = quotas.filter(dca__production_site_id=production_site_id)
    if feedstock_id:
        quotas = quotas.filter(feedstock_id=feedstock_id)
    if biofuel_id:
        quotas = quotas.filter(biofuel_id=biofuel_id)

    quotas = quotas.annotate(quota=Sum('approved_quota'))
    print(quotas)

    years = list(set([q['year'] for q in quotas]))
    biofuels = list(set([q['biofuel'] for q in quotas]))
    feedstocks = list(set([q['feedstock'] for q in quotas]))
    producers = list(set([q['dca__producer'] for q in quotas]))
    prodsites = list(set([q['dca__production_site'] for q in quotas]))
    consumed_quotas = LotTransaction.objects.filter(lot__carbure_producer__in=producers, lot__carbure_production_site__in=prodsites, lot__year__in=years, lot__biocarburant__in=biofuels, lot__matiere_premiere__in=feedstocks) \
        .values('lot__year', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__biocarburant', 'lot__matiere_premiere').annotate(volume=Sum('lot__volume'))
    print(consumed_quotas)
    data = []
    entry = {'producer': '', 'production_site': '', 'volume_produced': 1000, 'volume_allowed': 1500, 'quotas_full': 1, 'quotas_breached': 0, 'quotas_total': 9}
    return JsonResponse({'status': "success", 'data': data})

@check_rights('validator_entity_id', role=[UserRights.ADMIN, UserRights.RW])
def approve_dca(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.POST.get('dca_id', False)
    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)

    if entity.entity_type not in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
        return JsonResponse({'status': "error", 'message': "Not authorised"}, status=403)

    try:
        dca = DoubleCountingAgreement.objects.get(id=dca_id)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find DCA"}, status=400)

    # ensure all quotas have been validated
    remaining_quotas_to_check = DoubleCountingProduction.objects.filter(dca=dca, approved_quota=-1).count()
    if remaining_quotas_to_check > 0:
        return JsonResponse({'status': "error", 'message': "Some quotas have not been approved"}, status=400)

    if entity.name == 'DGPE':
        if not dca.status == DoubleCountingAgreement.INPROGRESS:
            return JsonResponse({'status': "error", 'message': "La DGEC doit valider le dossier en premier"}, status=400)
        dca.dgpe_validated = True
        dca.dgpe_validator = request.user
        dca.dgpe_validated_dt = pytz.utc.localize(datetime.datetime.now())
    elif entity.name == 'DGDDI':
        if not dca.status == DoubleCountingAgreement.INPROGRESS:
            return JsonResponse({'status': "error", 'message': "La DGEC doit valider le dossier en premier"}, status=400)        
        dca.dgddi_validated = True
        dca.dgddi_validator = request.user
        dca.dgddi_validated_dt = pytz.utc.localize(datetime.datetime.now())
    elif entity.entity_type == Entity.ADMIN:
        dca.dgec_validated = True
        dca.dgec_validator = request.user
        dca.dgec_validated_dt = pytz.utc.localize(datetime.datetime.now())
        dca.status = DoubleCountingAgreement.INPROGRESS
    else:
        return JsonResponse({'status': "error", 'message': "Unknown entity"}, status=400)
    if dca.dgpe_validated and dca.dgddi_validated and dca.dgec_validated:
        dca.status = DoubleCountingAgreement.ACCEPTED
        send_dca_status_email(dca)
    dca.save()
    return JsonResponse({'status': 'success'})

@check_rights('validator_entity_id', role=[UserRights.ADMIN, UserRights.RW])
def reject_dca(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.POST.get('dca_id', False)
    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)

    if entity.entity_type not in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]:
        return JsonResponse({'status': "error", 'message': "Not authorised"}, status=403)

    try:
        dca = DoubleCountingAgreement.objects.get(id=dca_id)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find DCA"}, status=400)

    if entity.name == 'DGPE':
        dca.dgpe_validated = False
        dca.dgpe_validator = request.user
        dca.dgpe_validated_dt = pytz.utc.localize(datetime.datetime.now())
    elif entity.name == 'DGDDI':
        dca.dgddi_validated = False
        dca.dgddi_validator = request.user
        dca.dgddi_validated_dt = pytz.utc.localize(datetime.datetime.now())
    elif entity.entity_type == Entity.ADMIN:
        dca.dgec_validated = False
        dca.dgec_validator = request.user
        dca.dgec_validated_dt = pytz.utc.localize(datetime.datetime.now())
    else:
        return JsonResponse({'status': "error", 'message': "Unknown entity"}, status=400)
    dca.status = DoubleCountingAgreement.REJECTED
    send_dca_status_email(dca)
    dca.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def remove_sourcing(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_sourcing_id = request.POST.get('dca_sourcing_id', False)

    if not dca_sourcing_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_sourcing_id"}, status=400)

    try:
        to_delete = DoubleCountingSourcing.objects.get(dca__producer=entity, id=dca_sourcing_id)
        if to_delete.dca.status == DoubleCountingAgreement.PENDING:
            to_delete.delete()
        else:
            return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find Sourcing Line"}, status=400)
    return JsonResponse({'status': "success"})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def remove_production(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_production_id = request.POST.get('dca_production_id', False)

    if not dca_production_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_production_id"}, status=400)

    try:
        to_delete = DoubleCountingProduction.objects.get(dca__producer=entity, id=dca_production_id)
        if to_delete.dca.status == DoubleCountingAgreement.PENDING:
            to_delete.delete()
        else:
            return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find Production Line"}, status=400)
    return JsonResponse({'status': "success"})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def add_sourcing(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.POST.get('dca_id', False)
    year = request.POST.get('year', False)
    metric_tonnes = request.POST.get('metric_tonnes', False)
    feedstock_code = request.POST.get('feedstock_code', False)
    origin_country_code = request.POST.get('origin_country_code', False)
    supply_country_code = request.POST.get('supply_country_code', False)
    transit_country_code = request.POST.get('transit_country_code', False)

    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)
    if not year:
        return JsonResponse({'status': "error", 'message': "Missing year"}, status=400)
    if not metric_tonnes:
        return JsonResponse({'status': "error", 'message': "Missing metric_tonnes"}, status=400)
    if not feedstock_code:
        return JsonResponse({'status': "error", 'message': "Missing feedstock_code"}, status=400)
    if not origin_country_code:
        return JsonResponse({'status': "error", 'message': "Missing origin_country_code"}, status=400)
    if not supply_country_code:
        return JsonResponse({'status': "error", 'message': "Missing supply_country_code"}, status=400)
    if not transit_country_code:
        return JsonResponse({'status': "error", 'message': "Missing transit_country_code"}, status=400)

    try:
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id, status=DoubleCountingAgreement.PENDING)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Could not find DCA"}, status=403)

    if dca.status != DoubleCountingAgreement.PENDING:
        return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)


    dcs = DoubleCountingSourcing()
    dcs.dca = dca
    dcs.year = year
    try:
        feedstock = MatierePremiere.objects.get(code=feedstock_code)
        dcs.feedstock = feedstock
    except:
        return JsonResponse({'status': "error", "message": "Could not find feedstock"}, status=400)

    try:
        oc = Pays.objects.get(code_pays=origin_country_code)
        dcs.origin_country = oc
    except:
        return JsonResponse({'status': "error", "message": "Could not find origin_country"}, status=400)
    try:
        sc = Pays.objects.get(code_pays=supply_country_code)
        dcs.supply_country = sc
    except:
        return JsonResponse({'status': "error", "message": "Could not find supply_country"}, status=400)
    try:
        tc = Pays.objects.get(code_pays=transit_country_code)
        dcs.transit_country = tc
    except:
        return JsonResponse({'status': "error", "message": "Could not find transit_country"}, status=400)
    dcs.metric_tonnes = metric_tonnes
    try:
        dcs.save()
    except:
        return JsonResponse({'status': "error", "message": "Could not save sourcing line"}, status=400)
    return JsonResponse({'status': "success"})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def add_production(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_id = request.POST.get('dca_id', False)
    year = request.POST.get('year', False)
    feedstock_code = request.POST.get('feedstock_code', False)
    biofuel_code = request.POST.get('biofuel_code', False)
    max_production_capacity = request.POST.get('max_production_capacity', False)
    estimated_production = request.POST.get('estimated_production', False)
    requested_quota = request.POST.get('requested_quota', False)

    if not dca_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_id"}, status=400)
    if not feedstock_code:
        return JsonResponse({'status': "error", 'message': "Missing feedstock_code"}, status=400)
    if not biofuel_code:
        return JsonResponse({'status': "error", 'message': "Missing biofuel_code"}, status=400)
    if not max_production_capacity:
        return JsonResponse({'status': "error", 'message': "Missing max_production_capacity"}, status=400)
    if not estimated_production:
        return JsonResponse({'status': "error", 'message': "Missing estimated_production"}, status=400)
    if not requested_quota:
        return JsonResponse({'status': "error", 'message': "Missing requested_quota"}, status=400)

    try:
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id, status=DoubleCountingAgreement.PENDING)
    except:
        return JsonResponse({'status': "forbidden", 'message': "Could not find DCA"}, status=403)

    if dca.status != DoubleCountingAgreement.PENDING:
        return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)


    dcp = DoubleCountingProduction()
    dcp.dca = dca
    dcp.year = year
    try:
        feedstock = MatierePremiere.objects.get(code=feedstock_code)
        dcp.feedstock = feedstock
    except:
        return JsonResponse({'status': "error", "message": "Could not find feedstock"}, status=400)
    try:
        biofuel = Biocarburant.objects.get(code=biofuel_code)
        dcp.biofuel = biofuel
    except:
        return JsonResponse({'status': "error", "message": "Could not find biofuel"}, status=400)

    dcp.max_production_capacity = max_production_capacity
    dcp.estimated_production = estimated_production
    dcp.requested_quota = requested_quota
    try:
        dcp.save()
    except:
        return JsonResponse({'status': "error", "message": "Could not save production line"}, status=400)
    return JsonResponse({'status': "success"})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def update_sourcing(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_sourcing_id = request.POST.get('dca_sourcing_id', False)
    metric_tonnes = request.POST.get('metric_tonnes', False)

    if not dca_sourcing_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_sourcing_id"}, status=400)
    if not metric_tonnes:
        return JsonResponse({'status': "error", 'message': "Missing metric_tonnes"}, status=400)

    try:
        to_update = DoubleCountingSourcing.objects.get(dca__producer=entity, id=dca_sourcing_id)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find Sourcing Line"}, status=400)
    if to_update.dca.status != DoubleCountingAgreement.PENDING:
        return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)

    to_update.metric_tonnes = metric_tonnes
    try:
        to_update.save()
    except:
        return JsonResponse({'status': "error", 'message': "Could not update Sourcing line"}, status=400)
    return JsonResponse({'status': "success"})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def update_production(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    dca_production_id = request.POST.get('dca_production_id', False)
    max_production_capacity = request.POST.get('max_production_capacity', False)
    estimated_production = request.POST.get('estimated_production', False)
    requested_quota = request.POST.get('requested_quota', False)

    if not dca_production_id:
        return JsonResponse({'status': "error", 'message': "Missing dca_production_id"}, status=400)

    try:
        to_update = DoubleCountingProduction.objects.get(dca__producer=entity, id=dca_production_id)
    except:
        return JsonResponse({'status': "error", 'message': "Could not find Production Line"}, status=400)
    if to_update.dca.status != DoubleCountingAgreement.PENDING:
        return JsonResponse({'status': "forbidden", 'message': "Agreement cannot be updated"}, status=403)
    if max_production_capacity:
        to_update.max_production_capacity = max_production_capacity
    if estimated_production:
        to_update.estimated_production = estimated_production
    if requested_quota:
        to_update.requested_quota = requested_quota
    try:
        to_update.save()
    except:
        return JsonResponse({'status': "error", 'message': "Could not update Production line"}, status=400)
    return JsonResponse({'status': "success"})


@is_admin
def admin_update_approved_quotas(request):
    approved_quotas = request.POST.get('approved_quotas', False)
    if not approved_quotas:
        return JsonResponse({'status': "error", 'message': "Missing approved_quotas POST parameter"}, status=400)
    unpacked = json.loads(approved_quotas)
    for (dca_production_id, approved_quota) in unpacked:
        try:
            to_update = DoubleCountingProduction.objects.get(id=dca_production_id)
            to_update.approved_quota = approved_quota
            to_update.save()
        except:
            return JsonResponse({'status': "error", 'message': "Could not find Production Line"}, status=400)
    return JsonResponse({'status': "success"})
