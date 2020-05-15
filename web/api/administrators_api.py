from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_administrators
from django.http import JsonResponse, HttpResponse
from core.models import Entity, Lot
from django.contrib.auth import get_user_model
from django.db.models import Q
import datetime
import io


# admin autocomplete helpers
@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_users_autocomplete(request, *args, **kwargs):
    q = request.GET.get('query', '')
    user_model = get_user_model()
    matches = user_model.objects.filter(Q(name__icontains=q) | Q(email__icontains=q))
    return JsonResponse({'suggestions': [{'value': '%s - %s' % (m.name, m.email), 'data': m.id} for m in matches]})


@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_entities_autocomplete(request, *args, **kwargs):
    q = request.GET.get('query', '')
    matches = Entity.objects.filter(name__icontains=q)
    return JsonResponse({'suggestions': [{'value': m.name, 'data': m.id} for m in matches]})


@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_lots(request, *args, **kwargs):
    lots = Lot.objects.all()
    lots = [{'carbure_id': k.carbure_id, 'producer_name': k.producer.name if k.producer else '',
             'producer_id': k.producer.id if k.producer else '',
             'production_site_name': k.production_site.name if k.production_site else '',
             'production_site_id': k.production_site.id if k.production_site else None, 'dae': k.dae,
             'ea_delivery_date': k.ea_delivery_date.strftime('%d/%m/%Y') if k.ea_delivery_date else '',
             'ea_delivery_site': k.ea_delivery_site, 'ea_name': k.ea.name if k.ea else '',
             'ea_id': k.ea.id if k.ea else None, 'volume': k.volume,
             'matiere_premiere_code': k.matiere_premiere.code if k.matiere_premiere else '',
             'matiere_premiere_name': k.matiere_premiere.name if k.matiere_premiere else '',
             'biocarburant_code': k.biocarburant.code if k.biocarburant else '',
             'biocarburant_name': k.biocarburant.name if k.biocarburant else '',
             'pays_origine_code': k.pays_origine.code_pays if k.pays_origine else '',
             'pays_origine_name': k.pays_origine.name if k.pays_origine else '', 'eec': k.eec, 'el': k.el, 'ep': k.ep,
             'etd': k.etd, 'eu': k.eu, 'esca': k.esca, 'eccs': k.eccs, 'eccr': k.eccr, 'eee': k.eee,
             'ghg_total': k.ghg_total, 'ghg_reference': k.ghg_reference, 'ghg_reduction': '%.2f%%' % (k.ghg_reduction),
             'client_id': k.client_id, 'status': k.status, 'ea_delivery_status': k.get_ea_delivery_status_display(),
             'lot_id': k.id} for k in lots]
    return JsonResponse(lots, safe=False)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def admin_lots_export(request, *args, **kwargs):
    today = datetime.datetime.now()
    filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))
    lots = Lot.objects.all(status="Validated")
    buffer = io.BytesIO()
    buffer.write("carbure_id;producer;production_site;volume;code_biocarburant;biocarburant;code_matiere_premiere;\
                  matiere_premiere;code_pays_origine;pays_origine;eec;el;ep;etd;eu;esca;eccs;eccr;eee;ghg_total;\
                  ghg_reference;ghg_reduction;dae;client_id;ea_delivery_date;ea;ea_delivery_site\n".encode())
    for k in lots:
        line = [k.carbure_id, k.producer.name if k.producer else '',
                k.production_site.name if k.production_site else '', k.volume,
                k.biocarburant.code if k.biocarburant else '', k.biocarburant.name if k.biocarburant else '',
                k.matiere_premiere.code if k.matiere_premiere else '',
                k.matiere_premiere.name if k.matiere_premiere else '',
                k.pays_origine.code_pays if k.pays_origine else '', k.pays_origine.name if k.pays_origine else '',
                k.eec, k.el, k.ep, k.etd, k.eu, k.esca, k.eccs, k.eccr, k.eee, k.ghg_total, k.ghg_reference,
                k.ghg_reduction, k.dae, k.client_id, k.ea_delivery_date, k.ea, k.ea_delivery_site]
    csvline = '%s\n' % (';'.join([str(li) for li in line]))
    buffer.write(csvline.encode('iso-8859-1'))
    csvfile = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="%s"' % (filename)
    response.write(csvfile)
    return response
