from django.db.models import Q
from django.http import JsonResponse
from core.models import LotTransaction
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays


sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name'}


def get_stocks(request):
    entity = request.GET.get('entity_id', False)
    production_sites = request.GET.getlist('production_sites')
    matieres_premieres = request.GET.getlist('matieres_premieres')
    countries_of_origin = request.GET.getlist('countries_of_origin')
    biocarburants = request.GET.getlist('biocarburants')
    delivery_sites = request.GET.getlist('delivery_sites')
    limit = request.GET.get('limit', None)
    from_idx = request.GET.get('from_idx', "0")
    query = request.GET.get('query', False)
    sort_by = request.GET.get('sort_by', False)
    order = request.GET.get('order', False)

    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Opérateur', 'Trader'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(carbure_client=entity)

    # filter by status
    txs = txs.filter(lot__status='Validated')

    # apply filters
    if production_sites:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) |
                         Q(lot__unknown_production_site__in=production_sites))
    if matieres_premieres:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if biocarburants:
        txs = txs.filter(lot__biocarburant__code__in=biocarburants)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if delivery_sites:
        txs = txs.filter(Q(carbure_delivery_site__in=delivery_sites) | Q(unknown_delivery_site__in=delivery_sites))

    if query:
        txs = txs.filter(Q(lot__matiere_premiere__name__icontains=query) |
                         Q(lot__biocarburant__name__icontains=query) |
                         Q(lot__carbure_producer__name__icontains=query) |
                         Q(lot__unknown_producer__icontains=query) |
                         Q(lot__carbure_id__icontains=query) |
                         Q(lot__pays_origine__name__icontains=query) |
                         Q(carbure_delivery_site__name__icontains=query) |
                         Q(unknown_delivery_site__icontains=query)
                         )

    if sort_by:
        if sort_by in sort_key_to_django_field:
            key = sort_key_to_django_field[sort_by]
            if order == 'desc':
                txs = txs.order_by('-%s' % key)
            else:
                txs = txs.order_by(key)
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown sort_by key'}, status=400)

    from_idx = int(from_idx)
    returned = txs[from_idx:]

    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    data = {}
    data['lots'] = [t.natural_key() for t in returned]
    data['total'] = len(txs)
    data['returned'] = len(returned)
    data['from'] = from_idx
    data['tx_errors'] = []
    data['lots_errors'] = []
    return JsonResponse({'status': 'success', 'data': data})


def get_snapshot(request):
    data = {}
    entity = request.GET.get('entity_id', False)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Trader', 'Opérateur'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(carbure_client=entity)

    mps = [{'value': m.code, 'label': m.name}
           for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]

    bcs = [{'value': b.code, 'label': b.name}
           for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]

    countries = [{'value': c.code_pays, 'label': c.name}
                 for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]

    ds1 = [c['carbure_delivery_site__name'] for c in txs.values('carbure_delivery_site__name').distinct()]
    ds2 = [c['unknown_delivery_site'] for c in txs.values('unknown_delivery_site').distinct()]
    delivery_sites = [s for s in ds1 + ds2 if s]

    ps1 = [p['lot__carbure_production_site__name'] for p in txs.values('lot__carbure_production_site__name').distinct()]
    ps2 = [p['lot__unknown_production_site'] for p in txs.values('lot__unknown_production_site').distinct()]
    psites = [p for p in ps1 + ps2 if p]

    data['filters'] = {'matieres_premieres': mps, 'biocarburants': bcs,
                       'production_sites': psites, 'countries_of_origin': countries, 'delivery_sites': delivery_sites}

    return JsonResponse({'status': 'success', 'data': data})
