from django.db.models.query_utils import Q
from django.http.response import JsonResponse

from core.models import GenericCertificate
from core.serializers import GenericCertificateSerializer


def get_certificates(request, *args, **kwargs):
    query = request.GET.get("query", "")
    objects = GenericCertificate.objects.filter(Q(certificate_id__icontains=query) | Q(certificate_holder__icontains=query))[
        0:100
    ]
    serializer = GenericCertificateSerializer(objects, many=True)
    return JsonResponse({"status": "success", "data": serializer.data})
