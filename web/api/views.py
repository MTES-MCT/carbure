from django.contrib.auth.decorators import login_required
from django.core import serializers
from core.decorators import enrich_with_user_details, restrict_to_producers, restrict_to_administrators, restrict_to_operators
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.db.models.fields import NOT_PROVIDED
import json
from core.models import *
from producers.models import *
from operators.models import *
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging
import datetime
import csv
from django.template import loader
import io
import random

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
  operators = Entity.objects.filter(entity_type='Opérateur', name__icontains=q)
  results = [{'value':i.name, 'data':i.id} for i in operators]
  return JsonResponse({'suggestions': results})

def biocarburant_csv(request):
  types = Biocarburant.objects.all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="biocarburants.csv"'
  writer = csv.writer(response, delimiter=';')
  writer.writerow(['biocarburant_code', 'biocarburant'])
  for t in types:
    writer.writerow([t.code, t.name])
  return response

def matiere_premiere_csv(request):
  types = MatierePremiere.objects.all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="matieres_premieres.csv"'
  writer = csv.writer(response, delimiter=';')
  writer.writerow(['matiere_premiere_code', 'matiere_premiere'])
  for t in types:
    writer.writerow([t.code, t.name])
  return response

def country_csv(request):
  types = Pays.objects.all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="pays.csv"'
  writer = csv.writer(response, delimiter=';')
  writer.writerow(['code_pays', 'pays'])
  for t in types:
    writer.writerow([t.code_pays, t.name])
  return response

def operators_csv(request):
  types = Entity.objects.filter(entity_type='Opérateur')
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="operateurs.csv"'
  writer = csv.writer(response, delimiter=';')
  writer.writerow(['ea'])
  for t in types:
    writer.writerow([t.name])
  return response

def get_random(model):
  max_id = model.objects.all().aggregate(max_id=Max("id"))['max_id']
  while True:
    pk = random.randint(1, max_id)
    element = model.objects.filter(pk=pk).first()
    if element:
      return element

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_import_csv_template(request, *args, **kwargs):
  context = kwargs['context']
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="template.csv"'
  writer = csv.writer(response, delimiter=';')
  writer.writerow(['production_site_name','volume','biocarburant_code','matiere_premiere_code','pays_origine_code','eec','el','ep','etd','eu','esca','eccs','eccr','eee','e','dae','client_id','ea_delivery_date','ea_name','ea_delivery_site'])
  psites = ProductionSite.objects.filter(producer=context['user_entity'])
  eas = Entity.objects.filter(entity_type='Opérateur')
  mps = MatierePremiere.objects.all()
  bcs = Biocarburant.objects.all()
  countries = Pays.objects.all()
  delivery_sites = ['Grandpuits', 'Le Havre', 'Tournefeuille', 'Guangzhou']
  volumes = [1200, 2800, 8000, 4500, 13000]
  clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
  today = datetime.date.today().strftime('%d/%m/%Y')
  for p in psites:
    mp = random.choice(mps)
    ea = random.choice(eas)
    bc = random.choice(bcs)
    country = random.choice(countries)
    site = random.choice(delivery_sites)
    volume = random.choice(volumes)
    writer.writerow([p.name,volume,bc.code,mp.code,country.code_pays,12,4,2,0,3.3,0,0,0,0,0,'DAE0000001',clientid,today,ea.name,site])
  return response

# producers
@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lots_drafts(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.filter(producer=context['user_entity'], status='Draft')
  lots_json = [{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots]

  errors = LotError.objects.filter(lot__in=lots)
  errors_json = [{'lot_id':e.lot.id, 'field':e.field, 'value':e.value, 'error':e.error} for e in errors]
  response =  {'lots': lots_json, 'errors': errors_json}
  return JsonResponse(response)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lots_corrections(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.filter(producer=context['user_entity'], ea_delivery_status__in=['AA', 'AC', 'R'])
  lots_json = [{'period':l.period, 'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots]

  response =  {'lots': lots_json}
  return JsonResponse(response)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lots_valid(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.filter(producer=context['user_entity'], status='Validated')
  lots_json = [{'period':l.period, 'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots]

  errors = LotError.objects.filter(lot__in=lots)
  errors_json = [{'lot_id':e.lot.id, 'field':e.field, 'value':e.value, 'error':e.error} for e in errors]
  response =  {'lots': lots_json, 'errors': errors_json}
  return JsonResponse(response)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lots_all(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.all(producer=context['user_entity'])
  lots_json = [{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots]

  errors = LotError.objects.filter(lot__in=lots)
  errors_json = [{'lot_id':e.lot.id, 'field':e.field, 'value':e.value, 'error':e.error} for e in errors]
  response =  {'lots': lots_json, 'errors': errors_json}
  return JsonResponse(response)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_corrections(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.filter(ea_delivery_status__in=['AC', 'AA', 'R'])
  return JsonResponse([{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots], safe=False)


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lot_save_comment(request, *args, **kwargs):
  context = kwargs['context']
  lot_id = request.POST.get('lot_id', None)
  comment = request.POST.get('comment', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Lot ID manquant'}, status=400)
  if not comment:
    return JsonResponse({'status':'error', 'message':'Veuillez entrer un commentaire'}, status=400)
  try:
    lot = Lot.objects.get(id=lot_id)
    lot.ea_delivery_status = 'AA'
    lot.save()
    lc = LotComment()
    lc.lot = lot
    lc.entity = context['user_entity']
    lc.comment = comment
    lc.save()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':'Erreur lors de l\'acceptation du lot', 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'lot comment saved'})

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
    outputs = ProductionSiteOutput.objects.filter(production_site__in=production_sites, biocarburant__name__icontains=q).values('biocarburant').distinct()
  else:
    outputs = ProductionSiteOutput.objects.filter(production_site=production_site, biocarburant__name__icontains=q).values('biocarburant').distinct()
  bcs = Biocarburant.objects.filter(id__in=outputs)
  return JsonResponse({'suggestions': [{'value':s.name, 'data':s.code} for s in bcs]})

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
    inputs = ProductionSiteInput.objects.filter(production_site__in=production_sites, matiere_premiere__name__icontains=q).values('matiere_premiere').distinct()
  else:
    inputs = ProductionSiteInput.objects.filter(production_site=production_site, matiere_premiere__name__icontains=q).values('matiere_premiere').distinct()
  mps = MatierePremiere.objects.filter(id__in=inputs)
  return JsonResponse({'suggestions': [{'value':s.name, 'data':s.code} for s in mps]})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_ges(request, *args, **kwargs):
  context = kwargs['context']
  mp = request.GET.get('mp', None)
  bc = request.GET.get('bc', None)
  if not mp or not bc:
    return JsonResponse({'status':'error', 'message':'Missing matiere premiere or biocarburant'}, status=400)
  mp = MatierePremiere.objects.get(code=mp)
  bc = Biocarburant.objects.get(code=bc)
  default_values = {'eec':0, 'el':0, 'ep':0, 'etd':0, 'eu':0.0, 'esca':0, 'eccs':0, 'eccr':0, 'eee':0, 'ghg_reference':83.8}
  try:
    ges = GHGValues.objects.filter(matiere_premiere=mp, biocarburant=bc).order_by('-ep_default')[0]
    default_values['eec'] = ges.eec_default
    default_values['ep'] = ges.ep_default
    default_values['etd'] = ges.etd_default
  except:
    pass
  return JsonResponse(default_values)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_duplicate_lot(request, *args, **kwargs):
  context = kwargs['context']
  lot_id = request.POST.get('lot_id', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Missing lot id'}, status=400)
  else:
    meta_fields = {f.name:f for f in Lot._meta.get_fields()}
    lot = Lot.objects.get(id=lot_id)
    lot.pk = None
    # hardcoded fields to remove
    fields_to_remove = ['carbure_id', 'dae', 'status', 'ea_delivery_status']
    # optional fields to remove (user configuration)
    fields_to_ignore = request.POST.getlist('fields[]')
    for f in fields_to_ignore:
      fields_to_remove.append(f)
    for f in fields_to_remove:
      if f in meta_fields:
        meta_field = meta_fields[f]
        if meta_field.default != NOT_PROVIDED:
          setattr(lot, f, meta_field.default)
        else:
          setattr(lot, f, '')
    lot.save()
    return JsonResponse({'status':'success', 'message':'OK, lot %d created' % (lot.id)})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_delete_lots(request, *args, **kwargs):
  context = kwargs['context']
  lot_ids = request.POST.get('lots', None)
  if not lot_ids:
    return JsonResponse({'status':'error', 'message':'Missing lot ids'}, status=400)
  try:
    ids = lot_ids.split(',')
    for lotid in ids:
      lot = Lot.objects.get(id=lotid, producer=context['user_entity'])
      lot.delete()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':'Could not delete lot', 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'lots deleted'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_validate_lots(request, *args, **kwargs):
  context = kwargs['context']
  lot_ids = request.POST.get('lots', None)
  if not lot_ids:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)

  ids = lot_ids.split(',')
  for lotid in ids:
    lot = Lot.objects.get(id=lotid, producer=context['user_entity'])
    # make sure all mandatory fields are set
    if not lot.dae:
      return JsonResponse({'status':'error', 'message':'Validation impossible. DAE manquant'}, status=400)
    if not lot.ea_delivery_site:
      return JsonResponse({'status':'error', 'message':'Validation impossible. Site de livraison manquant'}, status=400)
    if not lot.ea_delivery_date:
      return JsonResponse({'status':'error', 'message':'Validation impossible. Date de livraison manquante'}, status=400)
    if not lot.ea:
      return JsonResponse({'status':'error', 'message':'Validation impossible. Veuillez renseigner un client'}, status=400)
    if not lot.volume:
      return JsonResponse({'status':'error', 'message':'Validation impossible. Veuillez renseigner le volume du lot'}, status=400)
    if not lot.pays_origine:
      return JsonResponse({'status':'error', 'message':'Validation impossible. Veuillez renseigner le pays d\'origine de la matière première'}, status=400)
    try:
      today = datetime.date.today()
      lot = Lot.objects.get(id=lotid)
      # [PAYS][YYMM]P[IDProd]-[1....]-([S123])
      # FR2002P001-1
      lot.carbure_id = "%s%sP%d-%d" % ('FR', today.strftime('%y%m'), lot.producer.id, lot.id)
      lot.status = "Validated"
      lot.ea_delivery_status = 'AA'
      lot.save()
    except Exception as e:
      return JsonResponse({'status':'error', 'message':'Erreur lors de la validation du lot', 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'lots validated'})

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
def producers_settings_delete_mp(request, *args, **kwargs):
  context = kwargs['context']
  site = request.POST.get('site')
  mp = request.POST.get('matiere_premiere')

  if site == None:
    return JsonResponse({'status':'error', 'message':"Missing Site"}, status=400)
  if mp == None:
    return JsonResponse({'status':'error', 'message':"Missing MP"}, status=400)

  try:
    mp = MatierePremiere.objects.get(code=mp)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown MP", 'extra':str(e)}, status=400)

  try:
    ps = ProductionSite.objects.get(id=site, producer=context['user_entity'])
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown Production Site", 'extra':str(e)}, status=400)

  try:
    obj = ProductionSiteInput.objects.get(production_site=ps, matiere_premiere=mp)
    obj.delete()

  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'MP deleted'})

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_delete_biocarburant(request, *args, **kwargs):
  context = kwargs['context']
  site = request.POST.get('site')
  biocarburant = request.POST.get('biocarburant')

  if site == None:
    return JsonResponse({'status':'error', 'message':"Missing Site"}, status=400)
  if biocarburant == None:
    return JsonResponse({'status':'error', 'message':"Missing BC"}, status=400)

  try:
    biocarburant = Biocarburant.objects.get(code=biocarburant)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown BC", 'extra':str(e)}, status=400)

  try:
    ps = ProductionSite.objects.get(id=site, producer=context['user_entity'])
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown Production Site", 'extra':str(e)}, status=400)

  try:
    obj = ProductionSiteOutput.objects.get(production_site=ps, biocarburant=biocarburant)
    obj.delete()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'BC deleted'})



@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_save_lot(request, *args, **kwargs):
  context = kwargs['context']
  # new lot or edit?
  lot_id = request.POST.get('lot_id', None)
  if lot_id:
    try:
      lot = Lot.objects.get(id=lot_id)
    except Exception as e:
      return JsonResponse({'status':'error', 'message':"Lot inconnu", 'extra': str(e)}, status=400)
  else:
    # create empty lot
    lot = Lot()
    lot.save()

  lot.producer = context['user_entity']
  production_site_name = request.POST.get('production_site_name', None)
  try:
    lot.production_site = ProductionSite.objects.get(producer=context['user_entity'], name=production_site_name)
    LotError.objects.filter(lot=lot, field='production_site_name').delete()
  except:
    lot.production_site = None
    error, created = LotError.objects.update_or_create(lot=lot, field='production_site_name', error='Site de production inconnu', defaults={'value': production_site_name})

  biocarburant = request.POST.get('biocarburant_code', None)
  biocarburant_name = request.POST.get('biocarburant_name', None)
  try:
    lot.biocarburant = Biocarburant.objects.get(code=biocarburant)
    LotError.objects.filter(lot=lot, field='biocarburant_name').delete()
  except:
    lot.biocarburant = None
    if biocarburant_name:
      error, created = LotError.objects.update_or_create(lot=lot, field='biocarburant_name', error='Biocarburant inconnu', defaults={'value': biocarburant_name})
    elif biocarburant:
      error, created = LotError.objects.update_or_create(lot=lot, field='biocarburant_name', error='Biocarburant inconnu', defaults={'value': biocarburant})
    else:
      error, created = LotError.objects.update_or_create(lot=lot, field='biocarburant_name', error='Merci de préciser un biocarburant', defaults={'value': biocarburant})


  matiere_premiere = request.POST.get('matiere_premiere_code', None)
  matiere_premiere_name = request.POST.get('matiere_premiere_name', None)
  try:
    lot.matiere_premiere = MatierePremiere.objects.get(code=matiere_premiere)
    LotError.objects.filter(lot=lot, field='matiere_premiere_name').delete()
  except:
    lot.matiere_premiere = None
    if matiere_premiere_name:
      error, created = LotError.objects.update_or_create(lot=lot, field='matiere_premiere_name', error='Matière Première inconnue', defaults={'value': matiere_premiere_name})
    elif matiere_premiere:
      error, created = LotError.objects.update_or_create(lot=lot, field='matiere_premiere_name', error='Matière Première inconnue', defaults={'value': matiere_premiere})
    else:
      error, created = LotError.objects.update_or_create(lot=lot, field='matiere_premiere_name', error='Merci de préciser la matière première ', defaults={'value': matiere_premiere})

  volume = request.POST.get('volume', None)
  if volume:
    # no dots but commas, assume comma == dot
    if '.' not in volume:
      volume = volume.replace(',', '.')
    # dots and commas, assume commas are thousand separators
    if '.' in volume and ',' in volume:
      volume = volume.replace(',', '')
    lot.volume = float(volume)
    LotError.objects.filter(lot=lot, field='volume').delete()
  else:
    error, created = LotError.objects.update_or_create(lot=lot, field='volume', error='Merci de préciser un volume', defaults={'value': volume})

  pays_origine = request.POST.get('pays_origine_code', None)
  pays_origine_name = request.POST.get('pays_origine_name', None)
  try:
    lot.pays_origine = Pays.objects.get(code_pays=pays_origine)
    LotError.objects.filter(lot=lot, field='pays_origine_name').delete()
  except:
    lot.pays_origine = None
    if pays_origine_name:
      error, created = LotError.objects.update_or_create(lot=lot, field='pays_origine_name', error="Pays d'origine inconnu", defaults={'value': pays_origine_name})
    elif pays_origine:
      error, created = LotError.objects.update_or_create(lot=lot, field='pays_origine_name', error="Pays d'origine inconnu", defaults={'value': pays_origine})
    else:
      error, created = LotError.objects.update_or_create(lot=lot, field='pays_origine_name', error="Merci de choisir un pays d'origine", defaults={'value': pays_origine})

  eec = request.POST.get('eec', None)
  lot.eec = float(eec) if eec else 0.0
  el = request.POST.get('el', None)
  lot.el = float(el) if el else 0.0
  ep = request.POST.get('ep', None)
  lot.ep = float(ep) if ep else 0.0
  etd = request.POST.get('etd', None)
  lot.etd = float(etd) if etd else 0.0
  eu = request.POST.get('eu', None)
  lot.eu = float(eu) if eu else 0.0
  esca = request.POST.get('esca', None)
  lot.esca = float(esca) if esca else 0.0
  eccs = request.POST.get('eccs', None)
  lot.eccs = float(eccs) if eccs else 0.0
  eccr = request.POST.get('eccr', None)
  lot.eccr = float(eccr) if eccr else 0.0
  eee = request.POST.get('eee', None)
  lot.eee = float(eee) if eee else 0.0

  # calculs ghg
  lot.ghg_total = round(lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee, 2)
  lot.ghg_reference = 83.8
  lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)


  num_dae = request.POST.get('dae', None)
  if num_dae:
    lot.dae = num_dae
    LotError.objects.filter(lot=lot, field='dae').delete()
  else:
    error, created = LotError.objects.update_or_create(lot=lot, field='dae', error="Merci de préciser le numéro de DAE/DAU", defaults={'value': num_dae})

  ea_delivery_date = request.POST.get('ea_delivery_date', None)
  if not ea_delivery_date or ea_delivery_date == '':
    lot.ea_delivery_date = None
    lot.period = ''
    error, created = LotError.objects.update_or_create(lot=lot, field='ea_delivery_date', error="Merci de préciser la date de livraison", defaults={'value': None})
  else:
    try:
      edd = datetime.datetime.strptime(ea_delivery_date, '%d/%m/%Y')
      lot.ea_delivery_date = edd
      lot.period = edd.strftime('%Y-%M')
      LotError.objects.filter(lot=lot, field='ea_delivery_date').delete()
    except:
      error, created = LotError.objects.update_or_create(lot=lot, field='ea_delivery_date', error="Format de date incorrect: veuillez entrer une date au format JJ/MM/AAAA", defaults={'value': ea_delivery_date})

  ea_name = request.POST.get('ea_name', None)
  if ea_name:
    try:
      lot.ea = Entity.objects.get(name=ea_name)
      LotError.objects.filter(lot=lot, field='ea_name').delete()
    except:
      lot.ea = None
      error, created = LotError.objects.update_or_create(lot=lot, field='ea_name', defaults={'value': ea_name, 'error':"Client inconnu"})
  else:
    lot.ea = None
    error, created = LotError.objects.update_or_create(lot=lot, field='ea_name', defaults={'value': None, 'error':"Merci de préciser un client"})

  ea_delivery_site = request.POST.get('ea_delivery_site', None)
  if ea_delivery_site:
    lot.ea_delivery_site = ea_delivery_site
    LotError.objects.filter(lot=lot, field='ea_delivery_site').delete()
  else:
    error, created = LotError.objects.update_or_create(lot=lot, field='ea_delivery_site', error="Merci d'entrer un site de livraison", defaults={'value': None})

  client_id = request.POST.get('client_id', None)
  lot.client_id = client_id
  lot.save()

  errors = LotError.objects.filter(lot=lot)
  errors_json = [{'field':e.field, 'value':e.value, 'error':e.error} for e in errors]
  return JsonResponse({'status':'success', 'lot_id': lot.id, 'errors':errors_json})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_attestation_export(request, *args, **kwargs):
  context = kwargs['context']
  today = datetime.datetime.now()
  filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))
  lots = Lot.objects.all()
  buffer = io.BytesIO()
  buffer.write("carbure_id;producer;production_site;volume;code_biocarburant;biocarburant;code_matiere_premiere;matiere_premiere;code_pays_origine;pays_origine;eec;el;ep;etd;eu;esca;eccs;eccr;eee;ghg_total;ghg_reference;ghg_reduction;dae;client_id;ea_delivery_date;ea;ea_delivery_site\n".encode())
  for lot in lots:
    line = [lot.carbure_id,lot.producer.name if lot.producer else '',lot.production_site.name if lot.production_site else '',lot.volume,lot.biocarburant.code if lot.biocarburant else '',
            lot.biocarburant.name if lot.biocarburant else '',lot.matiere_premiere.code if lot.matiere_premiere else '',lot.matiere_premiere.name if lot.matiere_premiere else '',
            lot.pays_origine.code_pays if lot.pays_origine else '',lot.pays_origine.name if lot.pays_origine else '',lot.eec,lot.el,lot.ep,lot.etd,lot.eu,lot.esca,lot.eccs,
            lot.eccr,lot.eee,lot.ghg_total,lot.ghg_reference,lot.ghg_reduction,lot.dae,lot.client_id,lot.ea_delivery_date,lot.ea,lot.ea_delivery_site]
    csvline = '%s\n' % (';'.join([str(l) for l in line]))
    buffer.write(csvline.encode('iso-8859-1'))
  csvfile = buffer.getvalue()
  buffer.close()
  response = HttpResponse(content_type="text/csv")
  response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
  response.write(csvfile)
  return response

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lot_comments(request, *args, **kwargs):
  lot_id = request.POST.get('lot_id', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)
  else:
    comments = LotComment.objects.filter(lot_id=lot_id)
    return JsonResponse([{'comment':c.comment, 'from':c.entity.name if c.entity else ''} for c in comments], safe=False)

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_lot_errors(request, *args, **kwargs):
  lot_id = request.POST.get('lot_id', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)
  else:
    errors = LotError.objects.filter(lot_id=lot_id)
    return JsonResponse([{'field':e.field, 'value':e.value, 'error':e.error} for e in errors], safe=False)


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_declaration_export(request, *args, **kwargs):
  context = kwargs['context']
  declaration_id = kwargs['declaration_id']
  today = datetime.datetime.now()
  filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))
  declaration = OperatorDeclaration.objects.get(operator=context['user_entity'], id=declaration_id)
  lots = [l.lot for l in AcceptedLot.objects.filter(declaration=declaration)]
  buffer = io.BytesIO()
  buffer.write("carbure_id;producer;production_site;volume;code_biocarburant;biocarburant;code_matiere_premiere;matiere_premiere;code_pays_origine;pays_origine;eec;el;ep;etd;eu;esca;eccs;eccr;eee;ghg_total;ghg_reference;ghg_reduction;dae;client_id;ea_delivery_date;ea;ea_delivery_site\n".encode())
  for lot in lots:
    line = [lot.carbure_id,lot.producer.name if lot.producer else '',lot.production_site.name if lot.production_site else '',lot.volume,lot.biocarburant.code if lot.biocarburant else '',
            lot.biocarburant.name if lot.biocarburant else '',lot.matiere_premiere.code if lot.matiere_premiere else '',lot.matiere_premiere.name if lot.matiere_premiere else '',
            lot.pays_origine.code_pays if lot.pays_origine else '',lot.pays_origine.name if lot.pays_origine else '',lot.eec,lot.el,lot.ep,lot.etd,lot.eu,lot.esca,lot.eccs,
            lot.eccr,lot.eee,lot.ghg_total,lot.ghg_reference,lot.ghg_reduction,lot.dae,lot.client_id,lot.ea_delivery_date,lot.ea,lot.ea_delivery_site]
    csvline = '%s\n' % (';'.join([str(l) for l in line]))
    buffer.write(csvline.encode('iso-8859-1'))
  csvfile = buffer.getvalue()
  buffer.close()
  response = HttpResponse(content_type="text/csv")
  response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
  response.write(csvfile)
  return response

# operators api
@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lots_affilies(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.filter(ea=context['user_entity'], status='Validated').exclude(ea_delivery_status__in=['A', 'R'])
  return JsonResponse([{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id,
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date, 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots], safe=False)

# operators api
@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept(request, *args, **kwargs):
  context = kwargs['context']
  lot_ids = request.POST.get('lots', None)
  if not lot_ids:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)

  ids = lot_ids.split(',')
  for lotid in ids:
    lot = Lot.objects.get(id=lotid, ea=context['user_entity'])
    try:
      declaration = OperatorDeclaration.objects.get(operator=context['user_entity'], period=lot.attestation.period)
      accepted, created = AcceptedLot.objects.update_or_create(operator=context['user_entity'], declaration=declaration, lot=lot)
      lot.ea_delivery_status = 'A'
      lot.save()
    except Exception as e:
      return JsonResponse({'status':'error', 'message':'Erreur lors de l\'acceptation du lot', 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'lots accepted'})



@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept_correction(request, *args, **kwargs):
  context = kwargs['context']
  lot_id = request.POST.get('lot', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Lot ID manquant'}, status=400)
  lot = Lot.objects.get(id=lot_id, ea=context['user_entity'])
  lot.ea_delivery_status = 'A'
  lot.save()
  return JsonResponse({'status':'success', 'message':'lot accepted'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept_with_comment(request, *args, **kwargs):
  context = kwargs['context']
  lot_id = request.POST.get('lot', None)
  comment = request.POST.get('comment', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Lot ID manquant'}, status=400)
  if not comment:
    return JsonResponse({'status':'error', 'message':'Veuillez entrer un commentaire'}, status=400)
  lot = Lot.objects.get(id=lot_id, ea=context['user_entity'])
  try:
    declaration = OperatorDeclaration.objects.get(operator=context['user_entity'], period=lot.attestation.period)
    accepted, created = AcceptedLot.objects.update_or_create(operator=context['user_entity'], declaration=declaration, lot=lot)
    lot.ea_delivery_status = 'AC'
    lot.save()
    lc = LotComment()
    lc.lot = lot
    lc.entity = context['user_entity']
    lc.comment = comment
    lc.save()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':'Erreur lors de l\'acceptation du lot', 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'lot accepted'})

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_reject(request, *args, **kwargs):
  context = kwargs['context']
  lot_ids = request.POST.get('lots', None)
  comment = request.POST.get('comment', None)
  if not lot_ids:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)
  if not comment:
    return JsonResponse({'status':'error', 'message':'Veuillez entrer un commentaire'}, status=400)
  ids = lot_ids.split(',')
  for lotid in ids:
    lot = Lot.objects.get(id=lotid, ea=context['user_entity'])
    lot.ea_delivery_status = 'R'
    lot.save()
    lc = LotComment()
    lc.lot = lot
    lc.entity = context['user_entity']
    lc.comment = comment
    lc.save()
  return JsonResponse({'status':'success', 'message':'lots rejected'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lots(request, *args, **kwargs):
  context = kwargs['context']
  declaration_id = kwargs['declaration_id']
  acceptedlots = AcceptedLot.objects.filter(declaration_id=declaration_id)
  lots = [l.lot for l in acceptedlots]
  return JsonResponse([{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id,
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date, 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'status_display':l.get_status_display(), 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots], safe=False)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_comments(request, *args, **kwargs):
  lot_id = request.POST.get('lot_id', None)
  if not lot_id:
    return JsonResponse({'status':'error', 'message':'Aucun lot sélectionné'}, status=400)
  else:
    comments = LotComment.objects.filter(lot_id=lot_id)
    return JsonResponse([{'comment':c.comment, 'from':c.entity.name if c.entity else ''} for c in comments], safe=False)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_settings_add_depot(request, *args, **kwargs):
  context = kwargs['context']

  country = request.POST.get('country')
  name = request.POST.get('name')

  if country == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Pays"}, status=400)
  if name == None:
    return JsonResponse({'status':'error', 'message':"Veuillez entrer une valeur dans le champ Nom"}, status=400)

  try:
    country = Pays.objects.get(name__icontains=country)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Veuillez choisir un Pays dans la liste", 'extra':str(e)}, status=400)

  try:
    obj, created = OperatorDepot.objects.update_or_create(operator=context['user_entity'], country=country, name=name)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Depot added'})

# admin autocomplete helpers
@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_users_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET.get('query', '')
  user_model = get_user_model()
  matches = user_model.objects.filter(Q(name__icontains=q) | Q(email__icontains=q))
  return JsonResponse({'suggestions': [{'value':'%s - %s' % (m.name, m.email), 'data':m.id} for m in matches]})

@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_entities_autocomplete(request, *args, **kwargs):
  context = kwargs['context']
  q = request.GET.get('query', '')
  matches = Entity.objects.filter(name__icontains=q)
  return JsonResponse({'suggestions': [{'value':m.name, 'data':m.id} for m in matches]})


@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_lots(request, *args, **kwargs):
  context = kwargs['context']
  lots = Lot.objects.all()
  return JsonResponse([{'carbure_id': l.carbure_id, 'producer_name':l.producer.name if l.producer else '', 'producer_id':l.producer.id if l.producer else '',
  'production_site_name':l.production_site.name if l.production_site else '', 'production_site_id':l.production_site.id if l.production_site else None,
  'dae':l.dae, 'ea_delivery_date':l.ea_delivery_date.strftime('%d/%m/%Y') if l.ea_delivery_date else '', 'ea_delivery_site':l.ea_delivery_site, 'ea_name':l.ea.name if l.ea else '', 'ea_id':l.ea.id if l.ea else None,
  'volume':l.volume, 'matiere_premiere_code':l.matiere_premiere.code if l.matiere_premiere else '',
  'matiere_premiere_name':l.matiere_premiere.name if l.matiere_premiere else '', 'biocarburant_code':l.biocarburant.code if l.biocarburant else '',
  'biocarburant_name':l.biocarburant.name if l.biocarburant else '', 'pays_origine_code':l.pays_origine.code_pays if l.pays_origine else '',
  'pays_origine_name':l.pays_origine.name if l.pays_origine else '', 'eec':l.eec, 'el':l.el, 'ep':l.ep, 'etd':l.etd, 'eu':l.eu, 'esca':l.esca, 'eccs':l.eccs,
  'eccr':l.eccr, 'eee':l.eee, 'ghg_total':l.ghg_total, 'ghg_reference':l.ghg_reference, 'ghg_reduction':'%.2f%%' % (l.ghg_reduction), 'client_id':l.client_id,
  'status':l.status, 'ea_delivery_status':l.get_ea_delivery_status_display(), 'lot_id':l.id} for l in lots], safe=False)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_lots_export(request, *args, **kwargs):
  context = kwargs['context']
  today = datetime.datetime.now()
  filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))
  lots = [l.lot for l in AcceptedLot.objects.all()]
  buffer = io.BytesIO()
  buffer.write("carbure_id;producer;production_site;volume;code_biocarburant;biocarburant;code_matiere_premiere;matiere_premiere;code_pays_origine;pays_origine;eec;el;ep;etd;eu;esca;eccs;eccr;eee;ghg_total;ghg_reference;ghg_reduction;dae;client_id;ea_delivery_date;ea;ea_delivery_site\n".encode())
  for lot in lots:
    line = [lot.carbure_id,lot.producer.name if lot.producer else '',lot.production_site.name if lot.production_site else '',lot.volume,lot.biocarburant.code if lot.biocarburant else '',
            lot.biocarburant.name if lot.biocarburant else '',lot.matiere_premiere.code if lot.matiere_premiere else '',lot.matiere_premiere.name if lot.matiere_premiere else '',
            lot.pays_origine.code_pays if lot.pays_origine else '',lot.pays_origine.name if lot.pays_origine else '',lot.eec,lot.el,lot.ep,lot.etd,lot.eu,lot.esca,lot.eccs,
            lot.eccr,lot.eee,lot.ghg_total,lot.ghg_reference,lot.ghg_reduction,lot.dae,lot.client_id,lot.ea_delivery_date,lot.ea,lot.ea_delivery_site]
    csvline = '%s\n' % (';'.join([str(l) for l in line]))
    buffer.write(csvline.encode('iso-8859-1'))
  csvfile = buffer.getvalue()
  buffer.close()
  response = HttpResponse(content_type="text/csv")
  response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
  response.write(csvfile)
  return response