from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_operators
from operators.models import OperatorDeclaration

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_index(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-index'

  declarations = OperatorDeclaration.objects.filter(producer=context['user_entity'])
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
      OperatorDeclaration.objects.update_or_create(period=period, producer=context['user_entity'], defaults={'deadline':nextmonth})
      current_period -= datetime.timedelta(days=30)
    declarations = declarations.objects.filter(producer=context['user_entity'])

  context['declarations'] = declarations
  context['today'] = datetime.date.today()
  context['twoweeks'] = datetime.date.today() + datetime.timedelta(days=15)
  return render(request, 'operators/declarations.html', context)

@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_declaration(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'operators-declaration'
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
