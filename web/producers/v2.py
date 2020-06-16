from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index_v2(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'producers-index'
    return render(request, 'producers/attestation_v2.html', context)


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_mass_balance(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'producers-mb'
    return render(request, 'producers/mass_balance.html', context)


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_import_doc(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'producers-import-documentation'
    return render(request, 'producers/import_doc.html', context)


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_histo(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'producers-histo'
    return render(request, 'producers/archives.html', context)
