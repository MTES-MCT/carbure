from core.models import UserRights
from django.core.exceptions import PermissionDenied

def enrich_with_user_details(function):
    def wrap(request, *args, **kwargs):
        user_rights = UserRights.objects.filter(user=request.user)
        context = {}
        context['user_name'] = request.user.name
        context['nb_entities'] = len(user_rights)
        context['entities'] = [u.entity for u in user_rights]
        if len(user_rights) == 0:
            raise PermissionDenied
        context['user_entity'] = user_rights[0].entity
        context['user_entity_name'] = user_rights[0].entity.name
        kwargs['context'] = context
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def restrict_to_producers(function):
    def wrap(request, *args, **kwargs):
        context = kwargs['context']
        if context['user_entity'].entity_type != 'Producteur':
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_to_operators(function):
    def wrap(request, *args, **kwargs):
        context = kwargs['context']
        if context['user_entity'].entity_type != 'Opérateur':
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_to_administrators(function):
    def wrap(request, *args, **kwargs):
        context = kwargs['context']
        if context['user_entity'].entity_type != 'Administration':
            raise PermissionDenied
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap        