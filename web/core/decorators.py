from core.models import UserDetails, UserRights


def enrich_with_user_details(function):
    def wrap(request, *args, **kwargs):
        user_details = UserDetails.objects.get(user=request.user)
        user_rights = UserRights.objects.filter(user=user_details)
        context = {}
        context['user_name'] = user_details.user.name
        context['nb_entities'] = len(user_rights)
        context['entities'] = [u.entity for u in user_rights]
        context['user_entity'] = user_rights[0].entity.name
        kwargs['context'] = context
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
