from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_administrators
from django.http import JsonResponse
from core.models import Entity
from django.contrib.auth import get_user_model
from django.db.models import Q


# admin autocomplete helpers
@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_users_autocomplete(request, *args, **kwargs):
    q = request.GET.get('query', '')
    user_model = get_user_model()
    matches = user_model.objects.filter(Q(name__icontains=q) | Q(email__icontains=q))
    return JsonResponse({'suggestions': [{'value': '%s - %s' % (m.name, m.email), 'data': m.id} for m in matches]})


@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_entities_autocomplete(request, *args, **kwargs):
    q = request.GET.get('query', '')
    matches = Entity.objects.filter(name__icontains=q)
    return JsonResponse({'suggestions': [{'value': m.name, 'data': m.id} for m in matches]})
