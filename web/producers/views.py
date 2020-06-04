from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse_lazy
from producers.models import ProducerCertificate, ProductionSite, ProductionSiteInput, ProductionSiteOutput
from core.models import Lot, MatierePremiere, Pays, Biocarburant
from django.views.generic.edit import CreateView

import datetime
import calendar

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'producers-index'
  return render(request, 'producers/attestation.html', context)

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
  context['sites'] = ProductionSite.objects.filter(producer=context['user_entity'])
  mps = ProductionSiteInput.objects.filter(production_site__in=context['sites'])
  outputs = ProductionSiteOutput.objects.filter(production_site__in=context['sites'])
  certificates = ProducerCertificate.objects.filter(producer=context['user_entity'])
  for site in context['sites']:
    site.inputs = mps.filter(production_site=site)
    try:
      site.certificate = certificates.filter(production_site=site).order_by('-date_added')[0]
    except:
      site.certificate = None
    site.outputs = outputs.filter(production_site=site)
  return render(request, 'producers/settings.html', context)
