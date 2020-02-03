from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details
from django.shortcuts import render

@login_required
@enrich_with_user_details
def administrators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators_index-index'
  return render(request, 'administrators/attestations_admin.html', context)
