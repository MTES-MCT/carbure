from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_administrators
from django.shortcuts import render

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-index'
  return render(request, 'administrators/lots.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_annuaire(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-annuaire'
  return render(request, 'administrators/annuaire.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_controles(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-controles'
  return render(request, 'administrators/controles.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_suivi_corrections(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-suivi-corrections'
  return render(request, 'administrators/suivi_corrections.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-settings'
  return render(request, 'administrators/settings.html', context)
