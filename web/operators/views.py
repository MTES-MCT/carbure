from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_operators


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_index(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'operators-index'
    return render(request, 'operators/declarations_v2.html', context)


@login_required
@enrich_with_user_details
@restrict_to_operators
def operators_controles(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'operators-controles'
    return render(request, 'operators/controles.html', context)
