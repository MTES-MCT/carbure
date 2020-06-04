from django.contrib.auth.decorators import login_required
from core.decorators import enrich_with_user_details, restrict_to_producers
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse_lazy
from producers.models import ProducerCertificate, ProductionSite, ProductionSiteInput, ProductionSiteOutput
from core.models import Lot, MatierePremiere, Pays, Biocarburant
from django.views.generic.edit import CreateView

import datetime
import calendar


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_index_v2(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'producers-index-v2'
    return render(request, 'producers/attestation_v2.html', context)