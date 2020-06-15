from core.models import UserRights, UserPreferences, LotV2, LotTransaction, Lot
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def enrich_with_user_details(function):
    def wrap(request, *args, **kwargs):
        user_rights = UserRights.objects.filter(user=request.user)
        user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        if user_preferences.default_entity == None:
            if len(user_rights) == 0:
                return render(request, 'public/blank_user.html', {})
            default_right = user_rights[0]
            user_preferences.default_entity = default_right.entity
            user_preferences.save()
        context = {}
        context['user_name'] = request.user.name
        context['user'] = request.user
        context['nb_entities'] = len(user_rights)
        context['entities'] = [u.entity for u in user_rights]
        context['user_entity'] = user_preferences.default_entity
        context['user_entity_name'] = user_preferences.default_entity.name
        context['url_friendly_name'] = context['user_entity'].url_friendly_name()
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
        drafts = LotV2.objects.filter(added_by=context['user_entity'], status='Draft')
        valid = LotV2.objects.filter(added_by=context['user_entity'], status='Validated')
        corrections = LotTransaction.objects.filter(carbure_vendor=context['user_entity'], delivery_status__in=['AC', 'AA', 'R'])
        received = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='N', lot__status="Validated")
        accepted = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated")
        context['nb_corrections'] = len(corrections)
        context['nb_drafts'] = len(drafts)
        context['nb_valid'] = len(valid)
        context['nb_received'] = len(received)
        context['nb_mb'] = len(accepted)
        context['nb_controles_dgec'] = 0
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_to_operators(function):
    def wrap(request, *args, **kwargs):
        context = kwargs['context']
        if context['user_entity'].entity_type != 'Opérateur':
            raise PermissionDenied
        received = list(LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='N', lot__status="Validated"))
        received += list(LotTransaction.objects.filter(lot__added_by=context['user_entity'], lot__status="Draft"))
        context['nb_in'] = len(received)
        declared = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A')
        context['nb_mb'] = len(declared)
        out = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='N', lot__status="Validated")
        context['nb_out'] = len(out)
        context['nb_controles_dgec'] = 0
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