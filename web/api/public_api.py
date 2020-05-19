from core.models import Biocarburant, MatierePremiere, Pays, Entity, Depot
from django.http import JsonResponse, HttpResponse
import csv
from django.db.models import Q


# public
def biocarburant_autocomplete(request):
    q = request.GET['query']
    types = Biocarburant.objects.filter(name__icontains=q)
    results = [{'value': i.name, 'description': i.description, 'data': i.code} for i in types]
    return JsonResponse({'suggestions': results})


def matiere_premiere_autocomplete(request):
    q = request.GET['query']
    mps = MatierePremiere.objects.filter(name__icontains=q)
    results = [{'value': i.name, 'description': i.description, 'data': i.code} for i in mps]
    return JsonResponse({'suggestions': results})


def country_autocomplete(request):
    q = request.GET['query']
    countries = Pays.objects.filter(name__icontains=q)
    results = [{'value': i.name, 'data': i.code_pays} for i in countries]
    return JsonResponse({'suggestions': results})


def operators_autocomplete(request):
    q = request.GET['query']
    operators = Entity.objects.filter(entity_type='Opérateur', name__icontains=q)
    results = [{'value': i.name, 'data': i.id} for i in operators]
    return JsonResponse({'suggestions': results})


def depots_autocomplete(request):
    q = request.GET['query']
    depots = Depot.objects.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(depot_id__icontains=q))
    results = [{'value': '%s - %s - %s' % (i.name, i.depot_id, i.city), 'name': i.name, 'depot_id': i.depot_id, 'city':i.city} for i in depots]
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


def depots_csv(request):
    types = Depot.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="depots.csv"'
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['name', 'depot_id', 'city'])
    for t in types:
        writer.writerow([t.name, t.depot_id, t.city])
    return response
