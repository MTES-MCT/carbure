from django.http import JsonResponse

from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


def get_production_sites(request):
    q = request.GET.get("query", False)
    pid = request.GET.get("producer_id", False)
    psites = (
        ProductionSite.objects.select_related("country", "producer")
        .prefetch_related("productionsiteinput_set", "productionsiteoutput_set")
        .all()
        .order_by("name")
    )
    if q:
        psites = psites.filter(name__icontains=q)
    if pid:
        psites = psites.filter(producer__id=pid)

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    inputs = ProductionSiteInput.objects.select_related("matiere_premiere").filter(production_site__in=psites)
    for i in inputs:
        psitesbyid[i.production_site.id].inputs.append(i.matiere_premiere.natural_key())

    outputs = ProductionSiteOutput.objects.select_related("biocarburant").filter(production_site__in=psites)
    for o in outputs:
        psitesbyid[o.production_site.id].outputs.append(o.biocarburant.natural_key())
    sez = [
        {
            "name": p.name,
            "id": p.id,
            "country": p.country.natural_key(),
            "date_mise_en_service": p.date_mise_en_service,
            "ges_option": p.ges_option,
            "eligible_dc": p.eligible_dc,
            "dc_reference": p.dc_reference,
            "inputs": p.inputs,
            "outputs": p.outputs,
            "producer": p.producer.natural_key(),
        }
        for p in psites
    ]
    return JsonResponse({"status": "success", "data": sez})
