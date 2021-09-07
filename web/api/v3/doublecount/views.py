import datetime
import unicodedata
import xlsxwriter
from django.http import JsonResponse, HttpResponse
from core.decorators import check_rights, is_admin

from producers.models import ProductionSite
from doublecount.models import DoubleCountingAgreement, DoubleCountingSourcing, DoubleCountingProduction
from doublecount.serializers import DoubleCountingAgreementFullSerializer, DoubleCountingAgreementPartialSerializer
from doublecount.serializers import DoubleCountingAgreementFullSerializerWithForeignKeys, DoubleCountingAgreementPartialSerializerWithForeignKeys
from doublecount.helpers import load_dc_file, load_dc_sourcing_data, load_dc_production_data
from core.models import UserRights, MatierePremiere, Pays, Biocarburant
from core.xlsx_v3 import make_biofuels_sheet, make_dc_mps_sheet, make_countries_sheet, make_dc_production_sheet, make_dc_sourcing_sheet

@check_rights('entity_id')
def get_agreements(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    agreements = DoubleCountingAgreement.objects.filter(producer=entity)
    serializer = DoubleCountingAgreementPartialSerializer(agreements, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})

@is_admin
def get_agreements_admin(request, *args, **kwargs):
    entity_id = request.GET.get('entity_id', None)
    agreements = DoubleCountingAgreement.objects.all()
    if entity_id:
        agreements = agreements.filter(producer_id=entity_id)
    serializer = DoubleCountingAgreementFullSerializer(agreements, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})

@check_rights('entity_id')
def get_agreement(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    agreement_id = request.GET.get('dca_id', None)
    if not agreement_id:
        return JsonResponse({'status': 'error', 'message': 'Missing dca_id'}, status=400)
    try:
        agreement = DoubleCountingAgreement.objects.get(producer=entity, id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementPartialSerializerWithForeignKeys(agreement)
    return JsonResponse({'status': 'success', 'data': serializer.data})

@is_admin
def get_agreement_admin(request, *args, **kwargs):
    entity_id = request.GET.get('entity_id', None)
    agreement_id = request.GET.get('dca_id', None)

    if not entity_id:
        return JsonResponse({'status': 'error', 'message': 'Missing entity_id'}, status=400)
    if not agreement_id:
        return JsonResponse({'status': 'error', 'message': 'Missing dca_id'}, status=400)
    try:
        agreement = DoubleCountingAgreement.objects.filter(producer_id=entity_id, id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementFullSerializerWithForeignKeys(agreement)
    return JsonResponse({'status': 'success', 'data': serializer.data})



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

    dca, created = DoubleCountingAgreement.objects.get_or_create(producer=entity, production_site_id=production_site_id, period_start=start, period_end=end)

    try:
        load_dc_sourcing_data(dca, sourcing_data)
        load_dc_production_data(dca, production_data)
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({'status': "error", 'message': "File parsing error"}, status=400)


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

def approve_dca(request):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)

def reject_dca(request):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)


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
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id)
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
        dca = DoubleCountingAgreement.objects.get(producer=entity, id=dca_id)
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