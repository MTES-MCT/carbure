from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_administrators
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import ProducerCertificate

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
def administrators_suivi_certificats(request, *args, **kwargs):
  context = kwargs['context']
  context['certificates'] = ProducerCertificate.objects.all()
  context['current_url_name'] = 'administrators-suivi-certificats'
  return render(request, 'administrators/suivi_certificats.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_gestion_utilisateurs(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-gestion-utilisateurs'
  context['entities'] = Entity.objects.all()
  user_model = get_user_model()
  context['users'] = user_model.objects.all()
  context['user_rights'] = UserRights.objects.all()
  return render(request, 'administrators/gestion_utilisateurs.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'administrators-settings'
  return render(request, 'administrators/settings.html', context)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_validate_certificate(request, *args, **kwargs):
  context = kwargs['context']
  certificate_id = kwargs['id']
  try:
    certificate = ProducerCertificate.objects.get(id=certificate_id)
    certificate.status = 'Valid'
    certificate.save()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':'Could not find certificate'}, status=400)
  return redirect('administrators-suivi-certificats')
