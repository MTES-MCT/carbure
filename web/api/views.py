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
    [
		"19FRG0432000482724020",
		"GRANDPUITS",
		"1/10/2019",
		"28,687",
		"EMHV",
		"Colza",
		"CONV",
		"SV-2BS010010",
		"FR",
		"Oui",
		"1.00",
		"34.12",
		"83.80",
		"59.28%",
		"N/A",
		"FR",
		"1/7/2007",
		"Validé",
		"OperateurGamma",
		"""<input type="checkbox" />""",
    ]
   ]

  return JsonResponse({'data':sample_lots})