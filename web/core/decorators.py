from core.models import UserRights, Entity
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from functools import wraps
from itertools import chain

# check that request.POST contains an entity_id and request.user is allowed to make changes
def check_rights(entity_id_field, role=None):
    def actual_decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if not request.user.is_verified():
                return JsonResponse({'status': 'forbidden', 'message': "User not OTP verified"}, status=403)

            entity_id = request.POST.get(entity_id_field, request.GET.get(entity_id_field, False))
            if not entity_id:
                return JsonResponse({'status': 'error', 'message': "Missing field %s" % (entity_id_field)}, status=400)

            try:
                entity = Entity.objects.get(id=entity_id)
            except Exception:
                return JsonResponse({'status': 'error', 'message': "Unknown Entity id %s" % (entity_id)}, status=400)

            try:
                rights = UserRights.objects.get(user=request.user, entity=entity)
                if role is not None:
                    if isinstance(role, list):
                        if rights.role not in role:
                            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
                    elif role != rights.role:
                        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
                    else:
                        # all types of roles allowed
                        pass
            except:
                return JsonResponse({'status': 'forbidden', 'message': "User does not belong to entity"}, status=403)
            context = {}
            context['entity'] = entity
            kwargs['context'] = context
            return function(request, *args, **kwargs)
        return wrap
    return actual_decorator

def is_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'forbidden', 'message': "User not authenticated"}, status=403)
        if not request.user.is_verified():
            return JsonResponse({'status': 'forbidden', 'message': "User not verified"}, status=403)
        if not request.user.is_staff:
            return JsonResponse({'status': 'forbidden', 'message': "User not admin"}, status=403)
        return function(request, *args, **kwargs)
    return wrap

def is_admin_or_external_admin(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'forbidden', 'message': "User not authenticated"}, status=403)
        if not request.user.is_verified():
            return JsonResponse({'status': 'forbidden', 'message': "User not verified"}, status=403)
        ext_admins = Entity.objects.filter(entity_type=Entity.EXTERNAL_ADMIN)
        has_rights_to_ext_admin = UserRights.objects.filter(entity__in=ext_admins, user=request.user).count()
        if not request.user.is_staff and has_rights_to_ext_admin == 0:
            return JsonResponse({'status': 'forbidden', 'message': "User not admin"}, status=403)
        return function(request, *args, **kwargs)
    return wrap

def otp_or_403(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_verified():
            return JsonResponse({'status': 'forbidden', 'message': "User not verified"}, status=403)
        return function(request, *args, **kwargs)
    return wrap


# check that request.POST contains an entity_id and request.user is allowed to make changes
def check_user_rights(role=None):
    def actual_decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if not request.user.is_verified():
                return JsonResponse({'status': 'forbidden', 'message': "User not OTP verified"}, status=403)
            entity_id = request.POST.get('entity_id', request.GET.get('entity_id', False))
            if not entity_id:
                return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
            # check if we have data in the SESSION
            rights = request.session.get('rights', False)
            if not rights:
                rights = {str(ur.entity.id): ur.role for ur in UserRights.objects.filter(user=request.user)}
                request.session['rights'] = rights

            if entity_id not in rights:
                return JsonResponse({'status': 'forbidden', 'message': "User has no rights to the requested entity"}, status=403)

            if entity_id != request.session.get('entity_id', False):
                request.session['entity_id'] = entity_id

            user_role = rights[entity_id]
            if role is not None:
                if isinstance(role, list):
                    if user_role not in role:
                        return JsonResponse({'status': 'forbidden', 'message': "Insufficient rights to the requested entity"}, status=403)
                elif role != rights.role:
                    return JsonResponse({'status': 'forbidden', 'message': "Insufficient rights to the requested entity"}, status=403)
                else:
                    # all types of roles allowed
                    pass
            context = {}
            context['entity_id'] = request.session['entity_id']
            kwargs['context'] = context
            return function(request, *args, **kwargs)
        return wrap
    return actual_decorator


def is_auditor(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        entity_id = kwargs['context']['entity_id']
        try:
            Entity.objects.get(id=entity_id, entity_type=Entity.AUDITOR)
        except:
            return JsonResponse({'status': 'forbidden', 'message': "Entity is not auditor"}, status=403)
        return function(request, *args, **kwargs)
    return wrap
