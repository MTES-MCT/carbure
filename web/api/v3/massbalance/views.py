import datetime
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication


from api.v3.permissions import ReadPermission, ReadWritePermission
from core.models import UserRights
from core.decorators import check_rights
from core.xlsx_v3 import template_dae_to_upload 

from massbalance.models import OutTransaction
from massbalance.serializers import OutTransactionSerializer


class OutTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = OutTransactionSerializer
    permission_classes = [ReadPermission]
    authentication_classes = [SessionAuthentication]

    def get_queryset(self):
        entity_id = self.kwargs.get('entity_id')
        tx_status = self.kwargs.get('status')

        queryset = OutTransaction.objects.filter(vendor_id=entity_id)
        if tx_status == 'draft':
            queryset = queryset.filter(is_sent=False)
        elif tx_status == 'sent':
            queryset = queryset.filter(is_sent=False)
        elif tx_status == 'all':
            pass
        else:
            return Response(data="Unknown status %s" % (tx_status), status=status.HTTP_400_BAD_REQUEST)
        serializer = OutTransactionSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def create_dae(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']


@check_rights('entity_id')
def download_template(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    file_location = template_dae_to_upload(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_dae.xlsx"'
            return response
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def upload_dae_list(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # save file
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d'), entity.name.upper())
    filepath = '/tmp/%s' % (filename)
    with open(filepath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    nb_loaded, nb_total, errors = load_excel_file(entity, request.user, file, mass_balance=True)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    data = {'loaded': nb_loaded, 'total': nb_total}
    return JsonResponse({'status': 'success', 'data': data})


