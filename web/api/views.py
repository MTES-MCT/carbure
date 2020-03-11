from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.http import JsonResponse, HttpResponse
import json
from core.models import TypeBiocarburant, MatierePremiere, Pays

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
  sample_lots = [
    {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"28,687",
	 'type':"EMHV", 'matiere_premiere': "Colza", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"28,687",
	 'type':"EMHV", 'matiere_premiere': "Blé", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"2,687",
	 'type':"EMHV", 'matiere_premiere': "Blé", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "MY",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Brouillon", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"128,687",
	 'type':"EMHV", 'matiere_premiere': "Colza", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Brouillon", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"28,687",
	 'type':"EMHV", 'matiere_premiere': "Colza", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"28,687",
	 'type':"EMHV", 'matiere_premiere': "Colza", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
   ]

  return JsonResponse({'data':sample_lots})