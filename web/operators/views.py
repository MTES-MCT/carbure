from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_operators
from operators.models import OperatorDeclaration, AcceptedLot

import datetime
import calendar

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-index'

  declarations = OperatorDeclaration.objects.filter(operator=context['user_entity'])
  threemonthsago = datetime.date.today() - datetime.timedelta(days=90)
  last_declarations = declarations.filter(deadline__gte=threemonthsago)
  if len(last_declarations) <= 4:
    # create the missing 4 attestations
    current_period = datetime.date.today()
    current_period = current_period.replace(day=15)
    for i in range(5):
      period = current_period.strftime('%Y-%m')
      nextmonth = current_period + datetime.timedelta(days=30)
      monthrange = calendar.monthrange(nextmonth.year, nextmonth.month)
      nextmonth = nextmonth.replace(day=monthrange[1])
      # create attestation
      OperatorDeclaration.objects.update_or_create(period=period, operator=context['user_entity'], defaults={'deadline':nextmonth})
      current_period -= datetime.timedelta(days=30)
    declarations = OperatorDeclaration.objects.filter(operator=context['user_entity'])

  for declaration in declarations:
    declaration.lots = len(AcceptedLot.objects.filter(declaration=declaration))

  context['declarations'] = declarations
  context['today'] = datetime.date.today()
  context['twoweeks'] = datetime.date.today() + datetime.timedelta(days=15)
  return render(request, 'operators/declarations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_declaration(request, *args, **kwargs):
  context = kwargs['context']
  declaration_id = kwargs['declaration_id']
  context['current_url_name'] = 'operators-declaration'

  declarations = OperatorDeclaration.objects.filter(operator=context['user_entity'])
  current_declaration_qs = declarations.filter(id=declaration_id)
  if len(current_declaration_qs) == 0:
    raise PermissionDenied
  current_declaration = current_declaration_qs[0]
  next_declarations = declarations.filter(deadline__gt=current_declaration.deadline).order_by('deadline')
  previous_declarations = declarations.filter(deadline__lt=current_declaration.deadline).order_by('-deadline')
  context['current_declaration'] = current_declaration
  if len(next_declarations) == 0:
    # this is the latest attestation. no next, two previous
    context['next_declarations'] = None
    context['previous_declarations'] = previous_declarations[0:2]
  elif len(previous_declarations) == 0:
    # this is the first attestation. no previous, two next
    context['next_declarations'] = [next_declarations[1], next_declarations[0]]
    context['previous_declarations'] = None
  else:
    # middle, one of each
    context['next_declarations'] = [next_declarations[0]]
    context['previous_declarations'] = [previous_declarations[0]]

  return render(request, 'operators/declaration.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_lot(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-lot'
  return render(request, 'operators/lot.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_controles(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-controles'
  return render(request, 'operators/controles.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_affiliations(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-affiliations'
  return render(request, 'operators/affiliations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_settings(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-settings'
  return render(request, 'operators/settings.html', context)
