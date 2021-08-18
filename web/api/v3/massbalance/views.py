import datetime
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework import views, viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view

from api.v3.permissions import ReadPermission, ReadWritePermission
from core.models import UserRights
from core.decorators import check_rights
from core.xlsx_v3 import template_dae_to_upload 

from massbalance.models import OutTransaction
from massbalance.serializers import OutTransactionSerializer

def get_prefetched_data(entity_id=None):
    d['depots'] = {d.depot_id.lstrip('0').upper(): d for d in Depot.objects.all()}
    d['depotsbyname'] = {d.name.upper(): d for d in Depot.objects.all()}
    d['clients'] = {c.name.upper(): c for c in Entity.objects.filter(entity_type__in=['Producteur', 'Opérateur', 'Trader'])}    

def load_pending_transaction(transaction, pdata):
    client = transaction['client']
    if client and client.upper() in pdata['clients']:
        transaction['client_is_in_carbure'] = True
        transaction['carbure_client'] = pdata['clients'][client.upper()]
        transaction['unknown_client'] = ''
    else:
        transaction['client_is_in_carbure'] = False
        transaction['carbure_client'] = None
        transaction['unknown_client'] = client
    dsite = transaction['delivery_site']
    if dsite and dsite.upper() in pdata['depots']:
        transaction['delivery_site_is_in_carbure'] = True
        transaction['carbure_delivery_site'] = pdata['depots'][dsite.upper()]
        transaction['unknown_delivery_site'] = ''
    elif dsite and dsite.upper() in pdata['depotsbyname']:
        transaction['delivery_site_is_in_carbure'] = True
        transaction['carbure_delivery_site'] = pdata['depotsbyname'][dsite.upper()]
        transaction['unknown_delivery_site'] = ''
    else:
        transaction['delivery_site_is_in_carbure'] = False
        transaction['carbure_delivery_site'] = None
        transaction['unknown_delivery_site'] = dsite
    transaction['vendor'] = entity_id
    transaction['creation_method'] = 'USER'
    transaction['created_by'] = request.user
    serializer = OutTransactionCreateUpdateSerializer(data=transaction)
    if serializer.is_valid():
        obj = serializer.save()
        return obj
    return None

@api_view(['GET'])
def get_pending_transactions_list(request, *args, **kwargs):
    entity_id = request.query_params.get('entity_id')
    tx_status = request.query_params.get('tx_status', 'all')
    if not entity_id:
        return Response({'status': 'error', 'message': 'Missing entity_id'}, status=400)

    if not UserRights.objects.filter(user=request.user, entity_id=entity_id).exists():
        return Response({'status': 'error', 'message': 'Unauthorized'}, status=403)

    queryset = OutTransaction.objects.filter(vendor_id=entity_id)
    if tx_status == 'draft':
        queryset = queryset.filter(is_sent=False)
    elif tx_status == 'sent':
        queryset = queryset.filter(is_sent=False)
    elif tx_status == 'all':
        pass
    serializer = OutTransactionSerializer(queryset, context={'request':request}, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_pending_transactions(request, *args, **kwargs):
    entity_id = request.data.get('entity_id')
    transactions = request.data.get('transactions')
    if not entity_id:
        return Response({'status': 'error', 'message': 'Missing entity_id'}, status=400)
    if not UserRights.objects.filter(user=request.user, entity_id=entity_id).exists():
        return Response({'status': 'error', 'message': 'Unauthorized'}, status=403)

    pdata = get_prefetched_data()
    nb_submitted = 0
    nb_created = 0
    for transaction in transactions:
        obj = load_pending_transaction(transaction, pdata)
        nb_submitted += 1
        nb_created += 1 if obj else 0
    return Response({'status': 'success', 'data': {'submitted': nb_submitted, 'created': nb_created}}, status=status.HTTP_201_CREATED)


@check_rights('entity_id')
def download_template(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    file_location = template_dae_to_upload(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_dae.xlsx"'
            return response
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def upload_dae_list(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # save file
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d'), entity.name.upper())
    filepath = '/tmp/%s' % (filename)
    with open(filepath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    nb_loaded, nb_total, errors = load_excel_file(entity, request.user, file, mass_balance=True)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    data = {'loaded': nb_loaded, 'total': nb_total}
    return JsonResponse({'status': 'success', 'data': data})


