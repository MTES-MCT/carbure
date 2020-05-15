from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_operators
from django.http import JsonResponse, HttpResponse
from core.models import Lot, LotComment
import datetime
import io


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_export_lots(request, *args, **kwargs):
    context = kwargs['context']
    today = datetime.datetime.now()
    filename = 'export_%s.csv' % (today.strftime('%Y%m%d_%H%M%S'))
    lots = Lot.objects.filter(ea=context['user_entity'], ea_delivery_status='A')
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


# operators api
@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lots_affilies(request, *args, **kwargs):
    context = kwargs['context']
    lots = Lot.objects.filter(ea=context['user_entity'], status='Validated').exclude(ea_delivery_status__in=['A', 'R'])
    data = [{'period': k.period, 'carbure_id': k.carbure_id, 'producer_name': k.producer.name if k.producer else '',
             'producer_id': k.producer.id, 'production_site_name': k.production_site.name if k.production_site else '',
             'production_site_id': k.production_site.id if k.production_site else None, 'dae': k.dae,
             'ea_delivery_date': k.ea_delivery_date, 'ea_delivery_site': k.ea_delivery_site,
             'ea_name': k.ea.name if k.ea else '', 'ea_id': k.ea.id if k.ea else None, 'volume': k.volume,
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
    return JsonResponse(data, safe=False)


# operators api
@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept(request, *args, **kwargs):
    context = kwargs['context']
    lot_ids = request.POST.get('lots', None)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)

    ids = lot_ids.split(',')
    for lotid in ids:
        lot = Lot.objects.get(id=lotid, ea=context['user_entity'])
        try:
            lot.ea_delivery_status = 'A'
            lot.save()
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Erreur lors de l\'acceptation du lot', 'extra': str(e)},
                                status=400)
    return JsonResponse({'status': 'success', 'message': 'lots accepted'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept_correction(request, *args, **kwargs):
    context = kwargs['context']
    lot_id = request.POST.get('lot', None)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Lot ID manquant'}, status=400)
    lot = Lot.objects.get(id=lot_id, ea=context['user_entity'])
    lot.ea_delivery_status = 'A'
    lot.save()
    return JsonResponse({'status': 'success', 'message': 'lot accepted'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_accept_with_comment(request, *args, **kwargs):
    context = kwargs['context']
    lot_id = request.POST.get('lot', None)
    comment = request.POST.get('comment', None)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Lot ID manquant'}, status=400)
    if not comment:
        return JsonResponse({'status': 'error', 'message': 'Veuillez entrer un commentaire'}, status=400)
    lot = Lot.objects.get(id=lot_id, ea=context['user_entity'])
    try:
        lot.ea_delivery_status = 'AC'
        lot.save()
        lc = LotComment()
        lc.lot = lot
        lc.entity = context['user_entity']
        lc.comment = comment
        lc.save()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Erreur lors de l\'acceptation du lot', 'extra': str(e)},
                            status=400)
    return JsonResponse({'status': 'success', 'message': 'lot accepted'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_reject(request, *args, **kwargs):
    context = kwargs['context']
    lot_ids = request.POST.get('lots', None)
    comment = request.POST.get('comment', None)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)
    if not comment:
        return JsonResponse({'status': 'error', 'message': 'Veuillez entrer un commentaire'}, status=400)
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
    return JsonResponse({'status': 'success', 'message': 'lots rejected'})


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lots(request, *args, **kwargs):
    context = kwargs['context']
    lots = Lot.objects.filter(ea=context['user_entity'], ea_delivery_status='A')
    data = [{'period': k.period, 'carbure_id': k.carbure_id, 'producer_name': k.producer.name if k.producer else '',
             'producer_id': k.producer.id, 'production_site_name': k.production_site.name if k.production_site else '',
             'production_site_id': k.production_site.id if k.production_site else None, 'dae': k.dae,
             'ea_delivery_date': k.ea_delivery_date, 'ea_delivery_site': k.ea_delivery_site,
             'ea_name': k.ea.name if k.ea else '', 'ea_id': k.ea.id if k.ea else None, 'volume': k.volume,
             'matiere_premiere_code': k.matiere_premiere.code if k.matiere_premiere else '',
             'matiere_premiere_name': k.matiere_premiere.name if k.matiere_premiere else '',
             'biocarburant_code': k.biocarburant.code if k.biocarburant else '',
             'biocarburant_name': k.biocarburant.name if k.biocarburant else '',
             'pays_origine_code': k.pays_origine.code_pays if k.pays_origine else '',
             'pays_origine_name': k.pays_origine.name if k.pays_origine else '', 'eec': k.eec, 'el': k.el, 'ep': k.ep,
             'etd': k.etd, 'eu': k.eu, 'esca': k.esca, 'eccs': k.eccs, 'eccr': k.eccr, 'eee': k.eee,
             'ghg_total': k.ghg_total, 'ghg_reference': k.ghg_reference, 'ghg_reduction': '%.2f%%' % (k.ghg_reduction),
             'client_id': k.client_id, 'status': k.status, 'status_display': k.get_status_display(),
             'ea_delivery_status': k.get_ea_delivery_status_display(), 'lot_id': k.id} for k in lots]
    return JsonResponse(data, safe=False)


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot_comments(request, *args, **kwargs):
    lot_id = request.POST.get('lot_id', None)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)
    else:
        comments = LotComment.objects.filter(lot_id=lot_id)
        return JsonResponse([{'comment': c.comment, 'from': c.entity.name if c.entity else ''} for c in comments],
                            safe=False)
