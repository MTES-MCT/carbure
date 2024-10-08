from django.http import JsonResponse

from core.decorators import check_admin_rights
from transactions.models import ProductionSite


@check_admin_rights()
def get_entity_production_sites(request):
    company_id = request.GET.get("company_id", False)

    try:
        psites = ProductionSite.objects.filter(entitysite__entity_id=company_id)
        psitesbyid = {p.id: p for p in psites}
        for _k, v in psitesbyid.items():
            v.inputs = []
            v.outputs = []

        data = []

        for ps in psites:
            psite_data = ps.natural_key()
            psite_data["inputs"] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
            psite_data["outputs"] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
            certificates = []
            for pc in ps.productionsitecertificate_set.all():
                certificates.append(pc.natural_key())
            psite_data["certificates"] = certificates
            data.append(psite_data)

        return JsonResponse({"status": "success", "data": data})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find production sites"}, status=400)
