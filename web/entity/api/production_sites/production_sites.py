from django.http import JsonResponse

from core.serializers import GenericCertificateSerializer
from producers.models import ProductionSite
from core.decorators import check_rights


@check_rights("entity_id")
def get_production_sites(request, *args, **kwargs):
    context = kwargs["context"]
    psites = ProductionSite.objects.filter(producer=context["entity"])

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    data = []

    for ps in psites:
        psite_data = ps.natural_key()
        psite_data["inputs"] = [
            i.natural_key() for i in ps.productionsiteinput_set.all()
        ]
        psite_data["outputs"] = [
            o.natural_key() for o in ps.productionsiteoutput_set.all()
        ]
        psite_data["certificates"] = GenericCertificateSerializer(
            [p.certificate.certificate for p in ps.productionsitecertificate_set.all()],
            many=True,
        ).data
        data.append(psite_data)

    return JsonResponse({"status": "success", "data": data})
