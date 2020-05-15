from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details
from core.decorators import restrict_to_producers, restrict_to_administrators, restrict_to_operators
from django.http import JsonResponse, HttpResponse
from django.db.models.fields import NOT_PROVIDED
from core.models import Biocarburant, MatierePremiere, Pays, Entity, Lot
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
import datetime
import csv
import io


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