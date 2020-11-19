from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

from core.models import UserRights, UserPreferences, Entity

@login_required
@enrich_with_user_details
def set_default_entity(request, *args, **kwargs):
  context = kwargs['context']

  # get selected entity_id
  entity_id = kwargs['entity_id']
  # check if entity exists
  entity = Entity.objects.get(id=entity_id)
  # check if user is entitled to this entity
  right = UserRights.objects.filter(user=request.user, entity=entity)
  # set it as default
  if len(right) >= 1:
      UserPreferences.objects.update_or_create(user=request.user, defaults={'default_entity':entity})
      # return to home  
      return redirect('index')
  raise PermissionDenied
