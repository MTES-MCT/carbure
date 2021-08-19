from core.decorators import check_rights

from doublecount.models import DoubleCountingAgreement
from doublecount.serializers import DoubleCountingAgreementFullSerializer, DoubleCountingAgreementPartialSerializer
from doublecount.helpers import load_dc_file

@check_rights('entity_id')
def get_agreements(request, *args, **kwargs):
    agreements = DoubleCoutingAgreement.objects.filter(producer=entity)
    serializer = DoubleCountingAgreementPartialSerializer(agreements, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})

@is_admin
def get_agreements_admin(request, *args, **kwargs):
    entity_id = request.GET.get('entity_id', None)    
    agreements = DoubleCoutingAgreement.objects.all()
    if entity_id:
        agreements = agreements.filter(producer_id=entity_id)
    serializer = DoubleCountingAgreementFullSerializer(agreements, many=True)
    return JsonResponse({'status': 'success', 'data': serializer.data})

@check_rights('entity_id')
def get_agreement(request, *args, **kwargs):
    agreement_id = request.GET.get('dca_id', None)
    if not agreement_id:
        return JsonResponse({'status': 'error', 'message': 'Missing dca_id'}, status=400)
    try:
        agreement = DoubleCoutingAgreement.objects.filter(producer=entity, id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementPartialSerializer(agreement)
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
        agreement = DoubleCoutingAgreement.objects.filter(producer_id=entity_id, id=agreement_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find DCA agreement'}, status=400)
    serializer = DoubleCountingAgreementFullSerializer(agreement)
    return JsonResponse({'status': 'success', 'data': serializer.data})



@check_rights('entity_id')
def upload_file(request, *args, **kwargs):
    context = kwards['context']
    entity = context['entity']
    file_type = request.POST.get('file_type', None)
    if not file_type:
        return JsonResponse({'status': "error", 'message': "Missing file_type"}, status=400)
    
    f = request.FILES.get('file')
    if f is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # save file
    directory = '/tmp'
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d.%H%M%S'), entity.name.upper())
    filename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
    filepath = '%s/%s' % (directory, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

            
    if file_type == 'SOURCING':
        return load_dc_sourcing_file(entity, request.user, filepath)
    elif file_type == 'PRODUCTION':
        return load_dc_production_file(entity, request.user, filepath)
    elif file_type == 'RECOGNITION':
        return load_dc_recognition_file(entity, request.user, filepath)
    else:
        return JsonResponse({'status': 'error', 'message': 'unknown file_type'}, status=400)

def get_template(request):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)    

def approve_dca(request):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)        

def reject_dca(request):
    return JsonResponse({'status': 'error', 'message': 'not implemented'}, status=400)        
