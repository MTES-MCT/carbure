from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details


@login_required
@enrich_with_user_details
def producers_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-index'
  return render(request, 'producers/attestations.html', context)

@login_required
@enrich_with_user_details
def producers_inbox(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-inbox'
  return render(request, 'producers/inbox.html', context)

@login_required
@enrich_with_user_details
def producers_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-settings'
  return render(request, 'producers/settings.html', context)

@login_required
@enrich_with_user_details
def producers_attestation(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-attestation'
  return render(request, 'producers/attestation.html', context)

