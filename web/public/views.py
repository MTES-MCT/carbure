import datetime

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from core.models import UserRights, UserPreferences, MatierePremiere, Biocarburant, Lot, Entity
from core.decorators import enrich_with_user_details

def index(request):
  context = {}
  if request.user.is_authenticated:
    return redirect('home')
  return render(request, 'public/index.html', context)

@login_required
@enrich_with_user_details
def home(request, *args, **kwargs):
  context = kwargs['context']
  if context['user_entity'].entity_type == 'Administration':
    return redirect('administrators-index')
  elif context['user_entity'].entity_type == 'Producteur':
    return redirect('producers-index', producer_name=context['url_friendly_name'])
  elif context['user_entity'].entity_type == 'Opérateur':
    return redirect('operators-index', operator_name=context['url_friendly_name'])
  else:
    raise Http404("Unknown User Type")

def htmlreference(request):
  context = {}
  return render(request, 'common/reference.html', context)

@login_required
@enrich_with_user_details
def annuaire(request, *args, **kwargs):
  context = kwargs['context']
  context['current_url_name'] = 'annuaire'
  return render(request, 'common/annuaire.html', context)


def stats(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'public-stats'
    stats = []
    mps = {mp.code: mp for mp in MatierePremiere.objects.all()}
    carburants = {bc.code: bc for bc in Biocarburant.objects.all()}
    france = Pays.objects.get(code_pays='FR')
    today = datetime.date.today()
    since = datetime.date(year=today.year, month=1, day=1)
    stats_wanted = {'EMHV': ['COLZA', 'TOURNESOL', 'SOJA'],
                    'EMHU': ['HUILE_ALIMENTAIRE_USAGEE'],
                    'EMHA': ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2'],
                    'ET': ['BETTERAVE', 'BLE', 'MAIS', 'RESIDUS_VINIQUES']
                    }

    for c, mplist in stats_wanted.items():
        bc = carburants[c]
        for m in mplist:
            mp = mps[m]
            lots = Lot.objects.filter(status=Lot.VALID, matiere_premiere=mp, biocarburant=bc, ea_delivery_date__gte=since)
            vol_fr = lots.filter(pays_origine=france).aggregate(Sum('volume'))['volume__sum']
            vol_nfr = lots.exclude(pays_origine=france).aggregate(Sum('volume'))['volume__sum']
            if vol_fr is None:
                vol_fr = 0
            if vol_nfr is None:
                vol_nfr = 0
            co2 = (vol_fr + vol_nfr) * 23.4 * 83.8 * 0.5
            stats.append({'title': '%s de %s' % (bc.name, mp.name), 'vol_fr': vol_fr, 'vol_nfr': vol_nfr, 'bc_code': bc.code, 'mp_code': mp.code, 'eco_co2': '%.2f' % (co2 / 1000000.0)})
    context['stats'] = stats
    return render(request, 'public/stats.html', context)


def stats_details(request, *args, **kwargs):
    context = kwargs['context']
    context['current_url_name'] = 'public-stats'
    mp_code = kwargs['mp_code']
    bc_code = kwargs['bc_code']
    mp = MatierePremiere.objects.get(code=mp_code)
    bc = Biocarburant.objects.get(code=bc_code)
    context['biocarburant'] = '%s de %s' % (bc.name, mp.name)
    today = datetime.date.today()
    since = datetime.date(year=today.year, month=1, day=1)
    producers = {e.id: e for e in Entity.objects.filter(entity_type='Producteur')}
    summary = Lot.objects.filter(status=Lot.VALID, matiere_premiere=mp, biocarburant=bc, ea_delivery_date__gte=since).values('producer').order_by('producer').annotate(sum=Sum('volume'))
    stats = []
    for s in summary:
        stats.append({'producer': producers[s['producer']].name, 'vol': s['sum']})
    context['stats'] = stats
    return render(request, 'public/stats_details.html', context)