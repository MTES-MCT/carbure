from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details
from django.shortcuts import render

@login_required
@enrich_with_user_details
def administrators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-index'
  return render(request, 'administrators/lots.html', context)


@login_required
@enrich_with_user_details
def administrators_export(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-export'
  return render(request, 'administrators/export.html', context)

@login_required
@enrich_with_user_details
def administrators_controles(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-controles'
  return render(request, 'administrators/controles.html', context)


@login_required
@enrich_with_user_details
def administrators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-settings'
  return render(request, 'administrators/settings.html', context)
