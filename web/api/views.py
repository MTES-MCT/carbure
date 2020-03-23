from django.contrib.auth.decorators import login_required
from django.core import serializers
from core.decorators import enrich_with_user_details, restrict_to_producers, restrict_to_administrators
from django.http import JsonResponse, HttpResponse
import json
from core.models import *
from producers.models import *
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

# public 
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

def operators_autocomplete(request):
  q = request.GET['query']
  operators = Entity.objects.filter(entity_type='Operator', name__icontains=q)
  results = [{'value':i.name, 'data':i.id} for i in operators]
  return JsonResponse({'suggestions': results})

# producers
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
  return JsonResponse({'suggestions': [{'value':s.biocarburant.name, 'data':s.biocarburant.code} for s in outputs]})

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
  return JsonResponse({'suggestions': [{'value':s.matiere_premiere.name, 'data':s.matiere_premiere.code} for s in inputs]})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_ges(request, *args, **kwargs):
  context = kwargs['context']
  return JsonResponse({'eec':12, 'el':4, 'ep':2, 'etd':0, 'eu':3.3, 'esca':0, 'eccs':0, 'eccr':0, 'eee':0, 'ref':45})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_duplicate_lot(request, *args, **kwargs):
  context = kwargs['context']
  lot_id = request.POST.get('lot_id', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Missing lot id'}, status=400)
  else:
    lot = Lot.objects.get(id=lot_id)
    lot.pk = None
    lot.dae = ''
    lot.save()
    return JsonResponse({'status':'success', 'message':'OK'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_certif(request, *args, **kwargs):
  context = kwargs['context']
  
  certif_id = request.POST.get('certif_id')
  if certif_id == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Identifiant"}, status=400)

  form_exp_date = request.POST.get('expiration')
  if form_exp_date == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Expiration"}, status=400)
  try:
    exp_date = datetime.datetime.strptime(form_exp_date, '%d/%m/%Y')
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une date valide au format DD/MM/YYYY"}, status=400)

  site = request.POST.get('site')
  if site == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ  Site"}, status=400)
  try:
    site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Site de production inconnu"}, status=400)

  form_file = request.FILES.get('file', None)  
  if form_file == None:
    return JsonResponse({'status':'error', 'message':"Veuillez sélectionner un certificat (fichier PDF)"}, status=400)

  try:
    obj, created = ProducerCertificate.objects.update_or_create(producer=context['user_entity'], production_site=site, certificate_id=certif_id, defaults={'expiration':exp_date, 'certificate': form_file})
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Certificate added'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_delete_certif(request, *args, **kwargs):
  context = kwargs['context']
  
  certif_id = request.POST.get('certif_id')
  if certif_id == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Identifiant"}, status=400)

  try:
    crt = ProducerCertificate.objects.get(id=certif_id, producer=context['user_entity'])
    crt.delete()    
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Certificate deleted'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_site(request, *args, **kwargs):
  context = kwargs['context']
  
  country = request.POST.get('country')
  name = request.POST.get('name')
  date_mise_en_service = request.POST.get('date_mise_en_service')

  if country == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Pays"}, status=400)
  if name == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Nom"}, status=400)
  if date_mise_en_service == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une date dans le champ Date de mise en service"}, status=400)

  try:
    date_mise_en_service = datetime.datetime.strptime(date_mise_en_service, '%d/%m/%Y')
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une date valide au format DD/MM/YYYY"}, status=400)

  try:
    country = Pays.objects.get(name__icontains=country)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Veuillez choisir un Pays dans la liste", 'extra':str(e)}, status=400)

  try:
    obj, created = ProductionSite.objects.update_or_create(producer=context['user_entity'], country=country, name=name, defaults={'date_mise_en_service':date_mise_en_service})
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Site added'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_mp(request, *args, **kwargs):
  context = kwargs['context']
  
  site = request.POST.get('site')
  mp = request.POST.get('matiere_premiere')

  if site == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Site"}, status=400)
  if mp == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Matiere Premiere"}, status=400)

  try:
    mp = MatierePremiere.objects.get(code=mp)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Please provide a valid Matiere Premiere from the list", 'extra':str(e)}, status=400)

  try:
    site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Could not find production site in database"}, status=400)

  try:
    obj, created = ProductionSiteInput.objects.update_or_create(production_site=site, matiere_premiere=mp)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'MP added'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_biocarburant(request, *args, **kwargs):
  context = kwargs['context']
  site = request.POST.get('site')
  biocarburant = request.POST.get('biocarburant')

  if site == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Site"}, status=400)
  if biocarburant == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Biocarburant"}, status=400)

  try:
    biocarburant = Biocarburant.objects.get(code=biocarburant)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Please provide a valid Biocarburant from the list", 'extra':str(e)}, status=400)

  try:
    site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Could not find production site in database"}, status=400)

  try:
    obj, created = ProductionSiteOutput.objects.update_or_create(production_site=site, biocarburant=biocarburant)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Biocarburant added'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_save_lot(request, *args, **kwargs):
  context = kwargs['context']
  attestation_id = kwargs['attestation_id']

  # new lot or edit?
  lot_id = request.POST.get('lot_id', None)

  # mandatory fields
  production_site = request.POST.get('production_site', None)
  biocarburant = request.POST.get('biocarburant', None)
  matiere_premiere = request.POST.get('matiere_premiere', None)
  if not production_site or not biocarburant or not matiere_premiere:
    return JsonResponse({'status':'error', 'message':"Veuillez remplir au minimum les champs suivants: Site de Production, Biocarburant, Matière Première"}, status=400)

  # all other fields
  volume = request.POST.get('volume', None)
  pays_origine = request.POST.get('pays_origine', None)
  eec = request.POST.get('eec', None)
  el = request.POST.get('el', None)
  ep = request.POST.get('ep', None)
  etd = request.POST.get('etd', None)
  eu = request.POST.get('eu', None)
  esca = request.POST.get('esca', None)
  eccs = request.POST.get('eccs', None)
  eccr = request.POST.get('eccr', None)
  eee = request.POST.get('eee', None)

  num_dae = request.POST.get('num_dae', None)
  ea_delivery_date = request.POST.get('date_livraison', None)
  ea = request.POST.get('client', None)
  ea_delivery_site = request.POST.get('site_livraison', None)
  client_id = request.POST.get('client_id', None)

  if lot_id:
    lot = Lot.objects.get(id=lot_id)
  else:
    lot = Lot()
    
  lot.attestation = AttestationProducer.objects.get(id=attestation_id)
  lot.producer = context['user_entity']
  lot.production_site = ProductionSite.objects.get(id=production_site)

  lot.volume = float(volume)
  lot.matiere_premiere = MatierePremiere.objects.get(code=matiere_premiere)
  lot.biocarburant = Biocarburant.objects.get(code=biocarburant)
  lot.pays_origine = Pays.objects.get(code_pays=pays_origine)

  # ghg
  lot.eec = eec
  lot.el = el
  lot.ep = ep
  lot.etd = etd
  lot.eu = eu
  lot.esca = esca
  lot.eccs = eccs
  lot.eccr = eccr
  lot.eee = eee

  # client / delivery
  lot.dae = num_dae
  if not ea_delivery_date or ea_delivery_date == '':
    lot.ea_delivery_date = None
  else:
    lot.ea_delivery_date = ea_delivery_date
  lot.ea_delivery_site = ea_delivery_site
  if not ea or ea == '':
    lot.ea = None
  else:
    lot.ea = ea
  lot.client_id = client_id
  lot.save()
  return JsonResponse({'status':'success', 'lot_id': lot.id})

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
