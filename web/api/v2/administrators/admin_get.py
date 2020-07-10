from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q

from core.decorators import enrich_with_user_details, restrict_to_administrators

from core.models import LotTransaction, TransactionComment


@login_required
@enrich_with_user_details
@restrict_to_administrators
def get_out(request, *args, **kwargs):
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 25))
    search = request.GET.get('search[value]', None)

    if search != '':
        filtered = LotTransaction.objects.filter(lot__status='Validated').filter(Q(lot__matiere_premiere__name__icontains=search) |
                                                                                 Q(lot__biocarburant__name__icontains=search) |
                                                                                 Q(lot__carbure_producer__name__icontains=search) |
                                                                                 Q(lot__unknown_producer__icontains=search) |
                                                                                 Q(lot__carbure_id__icontains=search) |
                                                                                 Q(lot__pays_origine__name__icontains=search) |
                                                                                 Q(carbure_client__name__icontains=search) |
                                                                                 Q(unknown_client__icontains=search) |
                                                                                 Q(carbure_delivery_site__name__icontains=search) |
                                                                                 Q(unknown_delivery_site__icontains=search)
                                                                                 )
        transactions = filtered[start:start+length]
    else:
        filtered = LotTransaction.objects.filter(lot__status='Validated')[start:start+length]
        transactions = filtered
    comments = TransactionComment.objects.filter(tx__in=[t for t in transactions])
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    commentssez = serializers.serialize('json', comments, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez, 'comments': commentssez, 'recordsFiltered': len(filtered)})