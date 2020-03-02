from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_operators

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-index'
  return render(request, 'operators/declarations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_declaration(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-declaration'
  return render(request, 'operators/declaration.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-lot'
  return render(request, 'operators/lot.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_controles(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-controles'
  return render(request, 'operators/controles.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_annuaire(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-annuaire'
  return render(request, 'operators/annuaire.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_affiliations(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-affiliations'
  return render(request, 'operators/affiliations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-settings'
  return render(request, 'operators/settings.html', context)