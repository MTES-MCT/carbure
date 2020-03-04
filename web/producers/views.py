from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse_lazy
from producers.models import AttestationProducer, ProducerCertificate
from core.models import Lot, MatierePremiere
from django.views.generic.edit import CreateView

import datetime
import calendar

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-index'
  # create the last few attestations
  attestations = AttestationProducer.objects.filter(producer=context['user_entity'])
  threemonthsago = datetime.date.today() - datetime.timedelta(days=90)
  last_attestations = attestations.filter(deadline__gte=threemonthsago)
  if len(last_attestations) <= 4:
    # create the missing 4 attestations
    current_period = datetime.date.today()
    current_period = current_period.replace(day=15)
    for i in range(5):
      period = current_period.strftime('%Y-%m')
      nextmonth = current_period + datetime.timedelta(days=30)
      monthrange = calendar.monthrange(nextmonth.year, nextmonth.month)
      nextmonth = nextmonth.replace(day=monthrange[1])
      # create attestation
      AttestationProducer.objects.update_or_create(period=period, producer=context['user_entity'], defaults={'deadline':nextmonth})
      current_period -= datetime.timedelta(days=30)
    attestations = AttestationProducer.objects.filter(producer=context['user_entity'])

  for attestation in attestations:
    attestation.lots = len(Lot.objects.filter(attestation=attestation))
    attestation.drafts = len(Lot.objects.filter(attestation=attestation, status='Draft'))
    attestation.to_affiliate = len(Lot.objects.filter(attestation=attestation, status='Validated', affiliate=None))

  context['attestations'] = attestations
  context['today'] = datetime.date.today()
  context['twoweeks'] = datetime.date.today() + datetime.timedelta(days=15)
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
  context['certificates'] = ProducerCertificate.objects.filter(producer=context['user_entity'])
  return render(request, 'producers/settings.html', context)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_attestation(request, *args, **kwargs):
  context = kwargs['context']
  attestation_id = kwargs['attestation_id']
  context['current_url_name'] = 'producers-attestation'
  
  attestations = AttestationProducer.objects.filter(producer=context['user_entity'])
  current_attestation_qs = attestations.filter(id=attestation_id)
  if len(current_attestation_qs) == 0:
    raise PermissionDenied
  current_attestation = current_attestation_qs[0]
  next_attestations = attestations.filter(deadline__gt=current_attestation.deadline).order_by('deadline')
  previous_attestations = attestations.filter(deadline__lt=current_attestation.deadline).order_by('-deadline')
  context['current_attestation'] = current_attestation
  if len(next_attestations) == 0:
    # this is the latest attestation. no next, two previous
    context['next_attestations'] = None
    context['previous_attestations'] = previous_attestations[0:2]
  elif len(previous_attestations) == 0:
    # this is the first attestation. no previous, two next
    context['next_attestations'] = [next_attestations[1], next_attestations[0]]
    context['previous_attestations'] = None
  else:
    # middle, one of each
    context['next_attestations'] = [next_attestations[0]]
    context['previous_attestations'] = [previous_attestations[0]]

  lots = Lot.objects.filter(attestation=current_attestation)
  context['lots'] = lots
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

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_certif(request, *args, **kwargs):
  context = kwargs['context']
  # do something
  form_matiere_premiere = request.POST.get('matiere_premiere')
  if form_matiere_premiere == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Matiere Premiere"}, status=400)
  try:
    matiere_premiere = MatierePremiere.objects.get(name=form_matiere_premiere)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Could not find Matiere Premiere"}, status=400)

  form_exp_date = request.POST.get('expiration')
  if form_exp_date == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Expiration"}, status=400)
  try:
    exp_date = datetime.datetime.strptime(form_exp_date, '%d/%m/%Y')
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Please provide a valid Expiration Date DD/MM/YYYY"}, status=400)

  form_file = request.FILES.get('file', None)  
  if form_file == None:
    return JsonResponse({'status':'error', 'message':"Please provide a certificate file"}, status=400)

  try:
    obj, created = ProducerCertificate.objects.update_or_create(producer=context['user_entity'], matiere_premiere=matiere_premiere, defaults={'expiration':exp_date, 'certificate': form_file})
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Certificate added'})
