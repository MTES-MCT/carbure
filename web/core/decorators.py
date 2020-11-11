from core.models import UserRights, UserPreferences, LotV2, LotTransaction, TransactionComment, Entity
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import JsonResponse
from functools import wraps
from itertools import chain


# not an http endpoint
def get_producer_corrections(entity):
    # corrections de type "Durabilite" ou "Les deux" pour mes lots
    tx_added = LotTransaction.objects.filter(lot__data_origin_entity=entity, delivery_status__in=['R', 'AC', 'AA'], lot__status="Validated")
    comments_tx_added = TransactionComment.objects.filter(tx__in=tx_added, topic__in=['SUSTAINABILITY', 'BOTH'])
    # corrections de type "Transaction" ou "les deux" pour les lots vendus
    tx_sold = LotTransaction.objects.filter(carbure_vendor=entity, delivery_status__in=['R', 'AC', 'AA'], lot__status="Validated")
    comments_tx_sold = TransactionComment.objects.filter(tx__in=tx_sold, topic__in=['TX', 'BOTH'])
    # union de tout ça
    comments = set(list(chain(comments_tx_added, comments_tx_sold)))
    transactions = set([c.tx for c in comments])
    return transactions, comments


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
        drafts = LotTransaction.objects.filter(lot__added_by=context['user_entity'], lot__status='Draft')
        mb_drafts = LotV2.objects.filter(added_by=context['user_entity'], status='Draft').exclude(parent_lot=None)
        valid = LotV2.objects.filter(added_by=context['user_entity'], status='Validated')
        corrections, _ = get_producer_corrections(context['user_entity'])
        received = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")
        mb = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated", lot__fused_with=None)
        context['nb_corrections'] = len(corrections)
        context['nb_drafts'] = len(drafts)
        context['nb_mb_drafts'] = len(mb_drafts)
        context['nb_valid'] = len(valid)
        context['nb_in'] = len(received)
        context['nb_mb'] = len(mb)
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
        drafts = LotV2.objects.filter(added_by=context['user_entity'], status='Draft')
        received = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")
        declared = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated", lot__fused_with=None)
        context['nb_drafts'] = len(drafts)
        context['nb_in'] = len(received)
        context['nb_out'] = len(declared)
        context['nb_controles_dgec'] = 0
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def restrict_to_traders(function):
    def wrap(request, *args, **kwargs):
        context = kwargs['context']
        if context['user_entity'].entity_type != 'Trader':
            raise PermissionDenied
        drafts = LotV2.objects.filter(added_by=context['user_entity'], status='Draft')
        received = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")
        sent = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated", lot__fused_with=None)
        mb_drafts = LotV2.objects.filter(added_by=context['user_entity'], status='Draft').exclude(parent_lot=None)
        mb = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='A', lot__status="Validated", lot__fused_with=None)
        corrections, _ = get_producer_corrections(context['user_entity'])
        context['nb_drafts'] = len(drafts)
        context['nb_in'] = len(received)
        context['nb_out'] = len(sent)
        context['nb_mb'] = len(mb)
        context['nb_mb_drafts'] = len(mb_drafts)
        context['nb_corrections'] = len(corrections)
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


# check that request.POST contains an entity_id and request.user is allowed to make changes
def check_rights(entity_id_field):
    def actual_decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            entity_id = request.POST.get(entity_id_field, request.GET.get(entity_id_field, False))
            if not entity_id:
                return JsonResponse({'status': 'error', 'message': "Missing field %s" % (entity_id_field)}, status=400)

            try:
                entity = Entity.objects.get(id=entity_id)
            except Exception:
                return JsonResponse({'status': 'error', 'message': "Unknown Entity %s" % (entity_id)}, status=400)

            rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
            if entity not in rights:
                return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit entity"}, status=403)
            context = {}
            context['entity'] = entity
            kwargs['context'] = context
            return function(request, *args, **kwargs)
        return wrap
    return actual_decorator
