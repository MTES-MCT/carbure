import datetime
from django.http import JsonResponse
from core.decorators import is_admin
from django.contrib.auth import get_user_model
from core.models import Entity, UserRights
from django.db.models import Q
from django.contrib.auth.forms import PasswordResetForm

from core.models import LotTransaction
from api.v3.lots.helpers import get_lots_with_metadata, get_lots_with_errors, get_snapshot_filters


@is_admin
def get_users(request):
    q = request.GET.get('q', False)
    user_model = get_user_model()
    users = user_model.objects.all()
    if q:
        users = users.filter(Q(email__icontains=q) | Q(name__icontains=q))
    users_sez = [{'email': u.email, 'name': u.name, 'id': u.id} for u in users]
    return JsonResponse({"status": "success", "data": users_sez})


@is_admin
def get_entities(request):
    q = request.GET.get('q', False)
    entities = Entity.objects.all()
    if q:
        entities = entities.filter(name__icontains=q)
    entities_sez = [u.natural_key() for u in entities]
    return JsonResponse({"status": "success", "data": entities_sez})


@is_admin
def get_rights(request):
    q = request.GET.get('q', False)
    rights = UserRights.objects.all()
    if q:
        rights = rights.filter(Q(user__email__icontains=q) | Q(user__name__icontains=q) | Q(entity__name__icontains=q))
    rights_sez = [u.natural_key() for u in rights]
    return JsonResponse({"status": "success", "data": rights_sez})


@is_admin
def add_user(request):
    name = request.POST.get('name', False)
    email = request.POST.get('email', False)

    if not name:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field name"}, status=400)
    if not email:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Email"}, status=400)

    try:
        user_model = get_user_model()
        obj, created = user_model.objects.update_or_create(name=name, email=email)
        reset_password_form = PasswordResetForm(data={'email': email})
        if reset_password_form.is_valid():
            reset_password_form.save(request=request)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator", 'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'data': 'User created'})


@is_admin
def reset_user_password(request):
    uid = request.POST.get('user_id', False)

    if not uid:
        return JsonResponse({'status': 'error', 'message': "Please provide a user id"}, status=400)

    try:
        user_model = get_user_model()
        obj = user_model.objects.get(id=uid)
        reset_password_form = PasswordResetForm(data={'email': obj.email})
        if reset_password_form.is_valid():
            reset_password_form.save(request=request)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator", 'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'data': 'Password reset'})


@is_admin
def add_entity(request):
    name = request.POST.get('name', False)
    entity_type = request.POST.get('category', False)

    if not name:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field name"}, status=400)
    if not entity_type:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Category"}, status=400)

    if entity_type not in [c[0] for c in Entity.ENTITY_TYPES]:
        return JsonResponse({'status': 'error', 'message': "Unknown Category"}, status=400)

    try:
        obj, created = Entity.objects.update_or_create(name=name, entity_type=entity_type)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator", 'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'data': 'Entity created'})


@is_admin
def add_rights(request):
    user_id = request.POST.get('user_id', False)
    entity_id = request.POST.get('entity_id', False)

    if not user_id:
        return JsonResponse({'status': 'error', 'message': "Please provide a user_id"}, status=400)
    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Please provide an entity_id"}, status=400)

    user_model = get_user_model()
    try:
        user = user_model.objects.get(id=user_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find user"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find entity"}, status=400)

    try:
        obj, created = UserRights.objects.update_or_create(user=user, entity=entity)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator", 'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'data': 'User Right created'})


@is_admin
def delete_user(request):
    user_id = request.POST.get('user_id', False)

    if not user_id:
        return JsonResponse({'status': 'error', 'message': "Please provide a user_id"}, status=400)
    user_model = get_user_model()
    try:
        user = user_model.objects.get(id=user_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find user"}, status=400)

    user.delete()
    return JsonResponse({"status": "success", "data": "success"})

@is_admin
def delete_entity(request):
    entity_id = request.POST.get('entity_id', False)

    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Please provide an entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find entity"}, status=400)

    entity.delete()
    return JsonResponse({"status": "success", "data": "success"})

@is_admin
def delete_rights(request):
    right_id = request.POST.get('right_id', False)

    if not right_id:
        return JsonResponse({'status': 'error', 'message': "Please provide a right_id"}, status=400)
    try:
        right = UserRights.objects.get(id=right_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find right_id"}, status=400)

    right.delete()
    return JsonResponse({"status": "success", "data": "success"})


@is_admin
def get_lots(request):
    status = request.GET.get('status', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        txs = LotTransaction.objects.select_related(
            'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
            'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
            'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country'
        )

        txs = txs.filter(lot__status='Validated')

        if status == 'alert':
            txs, _ = get_lots_with_errors(txs)
        elif status == 'correction':
            txs = txs.filter(delivery_status__in=['AC', 'R', 'AA'])
        elif status == 'declaration':
            txs = txs.filter(delivery_status='A')

        return get_lots_with_metadata(txs, request.GET)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@is_admin
def get_snapshot(request):
    year = request.GET.get('year', False)

    today = datetime.date.today()
    date_from = today.replace(month=1, day=1)
    date_until = today.replace(month=12, day=31)

    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    try:
        data = {}
        txs = LotTransaction.objects.all().filter(lot__status='Validated')
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        _, total_errors = get_lots_with_errors(txs)
        correction = len(txs.filter(delivery_status__in=['AC', 'R', 'AA']))
        declaration= len(txs.filter(delivery_status='A'))
        data['lots'] = {'alert': total_errors, 'correction': correction, 'declaration': declaration}

        filters = get_snapshot_filters(txs)
        producers = Entity.objects.filter(entity_type='Producteur')
        operators = Entity.objects.filter(entity_type='Opérateur')
        traders = Entity.objects.filter(entity_type='Trader')

        filters['producers'] = [p.name for p in producers]
        filters['traders'] = [p.name for p in traders]
        filters['operators'] = [p.name for p in operators]

        data['filters'] = filters

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({"status": "success", "data": data})
