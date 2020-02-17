from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-index'
  return render(request, 'producers/attestations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_corrections(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-corrections'
  return render(request, 'producers/corrections.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_controles(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-controles'
  return render(request, 'producers/controles.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-settings'
  return render(request, 'producers/settings.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_attestation(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-attestation'
  return render(request, 'producers/attestation.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_export(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-export'
  return render(request, 'producers/export.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_annuaire(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-annuaire'
  return render(request, 'producers/annuaire.html', context)