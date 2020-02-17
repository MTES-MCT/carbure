from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details

@login_required
@enrich_with_user_details
def operators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-index'
  return render(request, 'operators/lots.html', context)

@login_required
@enrich_with_user_details
def operators_annuaire(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-annuaire'
  return render(request, 'operators/annuaire.html', context)

@login_required
@enrich_with_user_details
def operators_new_lots(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-new-lots'
  return render(request, 'operators/new_lots.html', context)

@login_required
@enrich_with_user_details
def operators_pending_lots(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-pending-lots'
  return render(request, 'operators/pending_lots.html', context)

@login_required
@enrich_with_user_details
def operators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-settings'
  return render(request, 'operators/settings.html', context)