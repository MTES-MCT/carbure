from django.http import JsonResponse
from core.decorators import is_admin
from django.contrib.auth import get_user_model
from core.models import Entity, UserRights
from django.db.models import Q
from django.contrib.auth.forms import PasswordResetForm


@is_admin
def get_users(request):
    query = request.POST.get('q', False)
    user_model = get_user_model()
    users = user_model.objects.all()
    if query:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(name__icontains=q))
    users_sez = [u.natural_key() for u in users]
    return JsonResponse({"status": "success", "data": users_sez})


@is_admin
def get_entities(request):
    query = request.POST.get('q', False)
    entities = Entity.objects.all()
    if query:
        entities = entities.filter(name__icontains=q)
    entities_sez = [u.natural_key() for u in entities]
    return JsonResponse({"status": "success", "data": entities_sez})


@is_admin
def get_rights(request):
    query = request.POST.get('q', False)
    rights = UserRights.objects.all()
    if query:
        rights = rights.filter(Q(user__username__icontains=q) | Q(user__email__icontains=q) | Q(user__name__icontains=q) | Q(entity__name__icontains=q))
    rights_sez = [r.natural_key() for u in rights]
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
