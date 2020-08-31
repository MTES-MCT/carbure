import datetime

from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_administrators
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays
from producers.models import ProducerCertificate, ProductionSiteInput, ProductionSiteOutput


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_index(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'administrators-index'
    return render(request, 'administrators/lots.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_controles(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'administrators-controles'
    return render(request, 'administrators/controles.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_suivi_corrections(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'administrators-suivi-corrections'
    return render(request, 'administrators/suivi_corrections.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_suivi_certificats(request, *args, **kwargs):
    context = kwargs['context']
    context['certificates'] = ProducerCertificate.objects.all()
    context['current_url_name'] = 'administrators-suivi-certificats'
    return render(request, 'administrators/suivi_certificats.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_certificate_details(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = kwargs['id']
    context['certificate'] = ProducerCertificate.objects.get(id=certificate_id)
    context['mps'] = ProductionSiteInput.objects.filter(production_site=context['certificate'].production_site)
    context['biocarburants'] = ProductionSiteOutput.objects.filter(production_site=context['certificate'].production_site)
    context['current_url_name'] = 'administrators-certificate-details'
    return render(request, 'administrators/details_certificate.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_gestion_utilisateurs(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'administrators-gestion-utilisateurs'
    context['all_entities'] = Entity.objects.all()
    context['entity_categories'] = Entity.ENTITY_TYPES
    user_model = get_user_model()
    context['users'] = user_model.objects.all()
    context['user_rights'] = UserRights.objects.all()
    return render(request, 'administrators/gestion_utilisateurs.html', context)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_validate_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = kwargs['id']
    try:
        certificate = ProducerCertificate.objects.get(id=certificate_id)
        certificate.status = 'Valid'
        certificate.save()
    except Exception as e:
        return JsonResponse({'status':'error', 'message':'Could not find certificate'}, status=400)
    return redirect('administrators-suivi-certificats')


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_validate_input(request, *args, **kwargs):
    context = kwargs['context']
    crtid = kwargs['crtid']
    input_id = kwargs['inputid']
    try:
        mp = ProductionSiteInput.objects.get(id=input_id)
        mp.status = 'Valid'
        mp.save()
    except Exception as e:
        return JsonResponse({'status':'error', 'message':'Could not find input in database'}, status=400)
    return redirect('administrators-certificate-details', id=crtid)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_validate_output(request, *args, **kwargs):
    context = kwargs['context']
    crtid = kwargs['crtid']
    output_id = kwargs['outputid']
    try:
        bc = ProductionSiteOutput.objects.get(id=output_id)
        bc.status = 'Valid'
        bc.save()
    except Exception as e:
        return JsonResponse({'status':'error', 'message':'Could not find output in database'}, status=400)
    return redirect('administrators-certificate-details', id=crtid)

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_delete_input(request, *args, **kwargs):
    context = kwargs['context']
    crtid = kwargs['crtid']
    input_id = kwargs['inputid']
    try:
        mp = ProductionSiteInput.objects.get(id=input_id)
        mp.delete()
    except Exception as e:
        return JsonResponse({'status':'error', 'message':'Could not find input in database'}, status=400)
    return redirect('administrators-certificate-details', id=crtid)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_delete_output(request, *args, **kwargs):
    context = kwargs['context']
    crtid = kwargs['crtid']
    output_id = kwargs['outputid']
    try:
        bc = ProductionSiteOutput.objects.get(id=output_id)
        bc.delete()
    except Exception as e:
        return JsonResponse({'status':'error', 'message':'Could not find output in database'}, status=400)
    return redirect('administrators-certificate-details', id=crtid)


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_add_entity(request, *args, **kwargs):
  context = kwargs['context']
  name = request.POST.get('name')
  entity_type = request.POST.get('category')

  if name == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field name"}, status=400)
  if entity_type == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Category"}, status=400)

  try:
    obj, created = Entity.objects.update_or_create(name=name, entity_type=entity_type)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'Entity created'})

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_add_user(request, *args, **kwargs):
  context = kwargs['context']
  name = request.POST.get('name')
  email = request.POST.get('email')

  if name == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field name"}, status=400)
  if email == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field Email"}, status=400)

  try:
    user_model = get_user_model()
    obj, created = user_model.objects.update_or_create(name=name, email=email)

    reset_password_form = PasswordResetForm(data={'email': email})
    if reset_password_form.is_valid():
      reset_password_form.save(request=request)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'User created'})

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_reset_user_password(request, *args, **kwargs):
  context = kwargs['context']
  uid = kwargs['uid']

  try:
    user_model = get_user_model()
    obj = user_model.objects.get(id=uid)
    reset_password_form = PasswordResetForm(data={'email': obj.email})
    if reset_password_form.is_valid():
      reset_password_form.save(request=request)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return redirect('administrators-gestion-utilisateurs')


@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_add_right(request, *args, **kwargs):
  context = kwargs['context']
  user_id = request.POST.get('user')
  entity_id = request.POST.get('entity')

  if user_id == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field user"}, status=400)
  if entity_id == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field entity"}, status=400)

  user_model = get_user_model()
  try:
    user = user_model.objects.get(id=user_id)
  except:
    return JsonResponse({'status':'error', 'message':"Could not find entity"}, status=400)

  try:
    entity = Entity.objects.get(id=entity_id)
  except:
    return JsonResponse({'status':'error', 'message':"Could not find entity"}, status=400)

  try:
    obj, created = UserRights.objects.update_or_create(user=user, entity=entity)
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'User Right created'})

@login_required
@enrich_with_user_details
@restrict_to_administrators
def administrators_delete_right(request, *args, **kwargs):
  context = kwargs['context']
  right_id = request.POST.get('right_id')

  if right_id == None:
    return JsonResponse({'status':'error', 'message':"Please provide a value in field UserRight"}, status=400)
  try:
    obj = UserRights.objects.get(id=right_id)
    obj.delete()
  except Exception as e:
    return JsonResponse({'status':'error', 'message':"Unknown error. Please contact an administrator", 'extra':str(e)}, status=400)
  return JsonResponse({'status':'success', 'message':'User Right deleted'})


@login_required
@enrich_with_user_details
@restrict_to_administrators
def alertes(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'administrators-alertes'
    return render(request, 'administrators/alertes.html', context)
