from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render

from producers.models import AttestationProducer
from core.models import Lot

import datetime
import calendar

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-index'
  # create the last 6 attestations
  attestations = AttestationProducer.objects.filter(producer=context['user_entity'])
  if len(attestations) < 6:
    # create the last 6 attestations
    current_period = datetime.date.today()
    current_period = current_period.replace(day=15)
    for i in range(7):
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