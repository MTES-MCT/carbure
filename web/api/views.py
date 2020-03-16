from django.contrib.auth.decorators import login_required
from django.core import serializers
from core.decorators import enrich_with_user_details, restrict_to_producers, restrict_to_administrators
from django.http import JsonResponse, HttpResponse
import json
from core.models import Biocarburant, MatierePremiere, Pays, Lot
from core.models import Entity
from django.contrib.auth import get_user_model
from django.db.models import Q


def biocarburant_autocomplete(request):
  q = request.GET.get('q', '')
  types = Biocarburant.objects.filter(name__icontains=q)
  results = [{'name':i.name, 'description':i.description} for i in types]
  data = json.dumps(results)
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

def matiere_premiere_autocomplete(request):
  q = request.GET.get('q', '')
  mps = MatierePremiere.objects.filter(name__icontains=q)
  results = [{'name':i.name, 'description':i.description} for i in mps]
  data = json.dumps(results)
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

def pays_autocomplete(request):
  q = request.GET.get('q', '')
  countries = Pays.objects.filter(name__icontains=q)
  results = [{'name':i.name, 'code_pays':i.code_pays} for i in countries]
  data = json.dumps(results)
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

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

@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_sample_lots(request, *args, **kwargs):
  context = kwargs['context']
  data = serializers.serialize('json', Lot.objects.all(), fields=('producer', 'production_site', 'dae', 'ea_delivery_date', 'ea_delivery_site', 'ea', 'volume',
    'matiere_premiere', 'biocarburant', 'pays_origine', 'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'e', 'ghg_reference', 'ghg_reduction',
    'client_id', 'status'), use_natural_foreign_keys=True)
  return HttpResponse(data, content_type='application/json')


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
