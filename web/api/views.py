from django.contrib.auth.decorators import login_required
from django.core import serializers
from core.decorators import enrich_with_user_details, restrict_to_producers, restrict_to_administrators
from django.http import JsonResponse, HttpResponse
import json
from core.models import Biocarburant, MatierePremiere, Pays, Lot, Entity
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

def biocarburant_autocomplete(request):
  q = request.GET['query']
  logging.info('[autocomplete] biocarburant: query [%s]' % (q))
  types = Biocarburant.objects.filter(name__icontains=q)
  results = [{'value':i.name, 'description':i.description, 'data':i.code} for i in types]
  return JsonResponse({'suggestions': results})

def matiere_premiere_autocomplete(request):
  q = request.GET['query']
  mps = MatierePremiere.objects.filter(name__icontains=q)
  results = [{'value':i.name, 'description':i.description, 'data':i.code} for i in mps]
  return JsonResponse({'suggestions': results})

def country_autocomplete(request):
  q = request.GET['query']
  countries = Pays.objects.filter(name__icontains=q)
  results = [{'value':i.name, 'data':i.code_pays} for i in countries]
  return JsonResponse({'suggestions': results})

@login_required
@enrich_with_user_details
def lot_save(request, *args, **kwargs):
  context = kwargs['context']
  return JsonResponse({'status':'success'})

@login_required
@enrich_with_user_details
def lot_validate(request, *args, **kwargs):
  context = kwargs['context']
  return JsonResponse({'status':'success'})

# producers autocomplete
@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_sample_lots(request, *args, **kwargs):
  context = kwargs['context']
  data = serializers.serialize('json', Lot.objects.all(), fields=('producer', 'production_site', 'dae', 'ea_delivery_date', 'ea_delivery_site', 'ea', 'volume',
    'matiere_premiere', 'biocarburant', 'pays_origine', 'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'e', 'ghg_reference', 'ghg_reduction',
    'client_id', 'status'), use_natural_foreign_keys=True)
  return HttpResponse(data, content_type='application/json')

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_prod_site_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET['query']
  producer_id = request.GET['producer_id']
  production_sites = ProductionSite.objects.filter(producer=producer_id, name__icontains=q)
  return JsonResponse({'suggestions': [{'value':s.name, 'data':s.id} for s in production_sites]})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_biocarburant_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET['query']
  producer_id = request.GET['producer_id']
  production_site = request.GET.get('production_site', None)
  if production_site == None:
    production_sites = ProductionSite.objects.filter(producer=producer_id)
    outputs = ProductionSiteOutput.objects.filter(production_site__in=production_sites, biocarburant__name__icontains=q)
  else:
    outputs = ProductionSiteOutput.objects.filter(production_site=production_site, biocarburant__name__icontains=q)
  return JsonResponse({'suggestions': [{'value':s.biocarburant.name, 'data':s.biocarburant.id} for s in outputs]})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_mp_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET['query']
  producer_id = request.GET['producer_id']
  production_site = request.GET.get('production_site', None)
  if production_site == None:
    production_sites = ProductionSite.objects.filter(producer=producer_id)
    inputs = ProductionSiteInput.objects.filter(production_site__in=production_sites, matiere_premiere__name__icontains=q)
  else:
    inputs = ProductionSiteInput.objects.filter(production_site=production_site, matiere_premiere__name__icontains=q)  
  return JsonResponse({'suggestions': [{'value':s.matiere_premiere.name, 'data':s.matiere_premiere.id} for s in inputs]})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_ges(request, *args, **kwargs):
  context = kwargs['context']
  return JsonResponse({'eec':12, 'el':4, 'ep':2, 'etd':0, 'eu':3.3, 'esca':0, 'eccs':0, 'eccr':0, 'eee':0, 'ref':45})

# admin autocomplete helpers

@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_users_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET.get('q', '')
  user_model = get_user_model()
  matches = user_model.objects.filter(Q(name__icontains=q) | Q(email__icontains=q))
  return JsonResponse({'suggestions': ['%s - %s' % (u.name, u.email) for u in matches]})

@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_entities_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET.get('q', '')
  matches = Entity.objects.filter(name__icontains=q)
  data = json.dumps({'suggestions': [m.name for m in matches]})
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)
