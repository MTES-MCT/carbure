from core.models import UserRights


def enrich_with_user_details(function):
    def wrap(request, *args, **kwargs):
        user_rights = UserRights.objects.filter(user=request.user)
        context = {}
        context['user_name'] = request.user.name
        context['nb_entities'] = len(user_rights)
        context['entities'] = [u.entity for u in user_rights]
        context['user_entity'] = user_rights[0].entity.name
        kwargs['context'] = context
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
