from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.http import JsonResponse

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
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"128,687",
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
     {'num_dae':"19FRG0432000482724020", 'site': "GRANDPUITS", "date_entree": "1/10/2019", 'volume':	"28,687",
	 'type':"EMHV", 'matiere_premiere': "Colza", 'systeme_fournisseur':	"SV-2BS010010", 'pays_origine': "FR",
	 'ges_transport_distribution':"1.00", 'ges_total':"34.12", 'ges_fossile':"83.80", 'ges_reductions':"59.28%",
	 'pays_implantation': "FR", 'date_mise_en_service':"1/7/2007", 'statut': "Validé", 'client':"OperateurGamma",
	 'checkbox': """<input type="checkbox" />"""
    },
   ]

  return JsonResponse({'data':sample_lots})