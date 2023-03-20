from core.models import UserRights, Entity, ExternalAdminRights
from django.http import JsonResponse
from django.db.models import Q
from core.common import ErrorResponse
from functools import wraps

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


class AdminRightsError:
    MISSING_ENTITY_ID = "MISSING_ENTITY_ID"
    USER_NOT_AUTHENTICATED = "USER_NOT_AUTHENTICATED"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    ENTITY_HAS_NO_RIGHT = "ENTITY_HAS_NO_RIGHT"
    ENTITY_NOT_ADMIN = "ENTITY_NOT_ADMIN"
    USER_NOT_ADMIN = "USER_NOT_ADMIN"
    USER_HAS_NO_RIGHT = "USER_HAS_NO_RIGHT"


#TODO sur les endpoints accessibles par des external admin, il faut en plus verifier qu'il n'agissent que sur les types d'entités autorisées (ex : DGAC sur companies aeriennes uniquement, cf get_entities) 
def check_admin_rights(allow_external=[], allow_role=None):
    def decorator(function_to_decorate):
        @wraps(function_to_decorate)
        def wrap(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return ErrorResponse(403, AdminRightsError.USER_NOT_AUTHENTICATED)

            if not request.user.is_verified():
                return ErrorResponse(403, AdminRightsError.USER_NOT_VERIFIED)

            entity_id = request.POST.get('entity_id', request.GET.get('entity_id', None))
            if entity_id is None:
                return ErrorResponse(400, AdminRightsError.MISSING_ENTITY_ID)

            try:
                # check that entity exists and is admin
                entity = Entity.objects.get(id=entity_id, entity_type__in=(Entity.ADMIN, Entity.EXTERNAL_ADMIN))
            except:
                return ErrorResponse(404, AdminRightsError.ENTITY_NOT_FOUND)

            try:
                # check that user has access to entity and refine by role if specified
                if allow_role is not None:
                    UserRights.objects.get(entity=entity, user=request.user, role__in=allow_role)
                else:
                    UserRights.objects.get(entity=entity, user=request.user)
            except:
                return ErrorResponse(403, AdminRightsError.USER_HAS_NO_RIGHT)

            # find out if the decorated function is accessible only by admins
            is_admin_only = len(allow_external) == 0

            # if the user tries to access an admin page
            if is_admin_only:
                # confirm that the current entity is the administration
                if entity.entity_type != Entity.ADMIN:
                    return ErrorResponse(403, AdminRightsError.ENTITY_NOT_ADMIN)
                # and confirm that the current user is part of the staff
                if not request.user.is_staff:
                    return ErrorResponse(403, AdminRightsError.USER_NOT_ADMIN)

            # for an external admin page, check that this entity can actually see it
            elif entity.entity_type == Entity.EXTERNAL_ADMIN:
                try:
                    ExternalAdminRights.objects.get(entity=entity, right__in=allow_external)
                except:
                    return ErrorResponse(403, AdminRightsError.ENTITY_HAS_NO_RIGHT)

            return function_to_decorate(request, *args, **kwargs)
        return wrap
    return decorator
