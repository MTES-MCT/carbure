from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from core.decorators import enrich_with_user_details, restrict_to_administrators

from core.models import LotTransaction, TransactionComment


@login_required
@enrich_with_user_details
@restrict_to_administrators
def get_out(request, *args, **kwargs):
    transactions = LotTransaction.objects.filter(lot__status='Validated')
    comments = TransactionComment.objects.filter(tx__in=transactions)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    commentssez = serializers.serialize('json', comments, use_natural_foreign_keys=True)
    return JsonResponse({'transactions': txsez, 'comments': commentssez})