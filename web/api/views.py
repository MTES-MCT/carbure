from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.http import JsonResponse, HttpResponse
import json
from core.models import TypeBiocarburant, MatierePremiere, Pays, Lot

def type_biocarburant_autocomplete(request):
  q = request.GET.get('q', '')
  types = TypeBiocarburant.objects.filter(name__icontains=q)
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
  sample_lots = Lot.objects.all()
  return JsonResponse({'data':sample_lots})