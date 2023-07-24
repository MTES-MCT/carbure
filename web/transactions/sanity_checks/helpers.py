import datetime
from certificates.models import DoubleCountingRegistration
from ml.models import EECStats, EPStats, ETDStats
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from transactions.models.locked_year import LockedYear
from core.models import (
    Biocarburant,
    CarbureLot,
    Depot,
    Entity,
    EntityCertificate,
    EntityDepot,
    GenericCertificate,
    GenericError,
    MatierePremiere,
    Pays,
)

july1st2021 = datetime.date(year=2021, month=7, day=1)


# quickly create a lot error
def generic_error(error, **kwargs):
    d = {
        "display_to_creator": True,
        "display_to_admin": True,
        "display_to_auditor": True,
        "error": error,
    }
    d.update(kwargs)
    return GenericError(**d)


# check if there are some blocking errors in the given list
def has_blocking_errors(errors: list[GenericError]):
    for e in errors:
        if e.is_blocking:
            return True
    return False


# check if the lot is bound to RED II rules
def is_red_ii(lot: CarbureLot):
    if not lot.delivery_date:
        return True
    return lot.delivery_date >= july1st2021


# check if the lot is a delivery to france
def is_french_delivery(lot: CarbureLot):
    return (
        lot.delivery_type
        in [
            CarbureLot.BLENDING,
            CarbureLot.TRADING,
            CarbureLot.STOCK,
            CarbureLot.DIRECT,
            CarbureLot.UNKNOWN,
        ]
        and lot.delivery_site_country
        and lot.delivery_site_country.code_pays == "FR"
    )


# check if the given error is found in the list
def has_error(error, error_list):
    for e in error_list:
        if e.error == error:
            return True
    return False


# select data related to a lot to speed up sanity checks
def enrich_lot(lot):
    queryset = CarbureLot.objects.filter(id=lot.id).select_related(
        "carbure_producer",
        "carbure_supplier",
        "carbure_client",
        "added_by",
        "carbure_production_site",
        "carbure_production_site__producer",
        "carbure_production_site__country",
        "production_country",
        "carbure_dispatch_site",
        "carbure_dispatch_site__country",
        "dispatch_site_country",
        "carbure_delivery_site",
        "carbure_delivery_site__country",
        "delivery_site_country",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "parent_stock",
        "parent_lot",
    )
    return queryset.get()


def get_prefetched_data(entity=None):
    data = {
        "countries": {},
        "biofuels": {},
        "depots": {},
        "depotsbyname": {},
        "locked_years": [],
        "my_production_sites": {},
        "my_vendor_certificates": [],
        "depotsbyentity": {},
        "entity_certificates": {},
        "production_sites": {},
        "clients": {},
        "clientsbyname": {},
        "certificates": {},
        "double_counting_certificates": {},
        "etd": {},
        "eec": {},
        "ep": {},
        "checked_certificates": {},
    }

    data["countries"] = {p.code_pays: p for p in Pays.objects.all()}
    data["biofuels"] = {b.code: b for b in Biocarburant.objects.all()}
    data["feedstocks"] = {m.code: m for m in MatierePremiere.objects.all()}
    data["depots"] = {d.depot_id: d for d in Depot.objects.all()}
    data["depotsbyname"] = {d.name.upper(): d for d in data["depots"].values()}
    data["locked_years"] = [locked_year.year for locked_year in LockedYear.objects.filter(locked=True)]

    if entity:
        # get only my production sites
        entity_psites = ProductionSite.objects.filter(producer=entity).prefetch_related("productionsiteinput_set", "productionsiteoutput_set", "productionsitecertificate_set")  # fmt:skip
        data["my_production_sites"] = {ps.name.upper(): ps for ps in entity_psites}

        # get all my linked certificates
        entity_certs = EntityCertificate.objects.filter(entity=entity)
        data["my_vendor_certificates"] = [c.certificate.certificate_id for c in entity_certs]

    # MAPPING OF ENTITIES AND DELIVERY SITES
    # dict {'entity1': [depot1, depot2], 'entity2': [depot42]}
    depotsbyentities = dict()
    associated_depots = EntityDepot.objects.select_related("entity", "depot").all()
    for entitydepot in associated_depots.iterator():
        if entitydepot.entity.pk in depotsbyentities:
            depotsbyentities[entitydepot.entity.pk].append(entitydepot.depot.depot_id)
        else:
            depotsbyentities[entitydepot.entity.pk] = [entitydepot.depot.depot_id]
    data["depotsbyentity"] = depotsbyentities

    # MAPPING OF ENTITIES AND THEIR CERTIFICATES
    # dict {'entity1': {'cert1_id': cert1, 'cert2_id': cert2}, 'entity2': {'cert14_id': cert14}}
    entity_certificates = {}
    certificates = EntityCertificate.objects.select_related("entity", "certificate").all()
    for entitycertificate in certificates.iterator():
        if entitycertificate.entity.pk not in entity_certificates:
            entity_certificates[entitycertificate.entity.pk] = {}
        entity_certificates[entitycertificate.entity.pk][entitycertificate.certificate.certificate_id] = entitycertificate
    data["entity_certificates"] = entity_certificates

    # MAPPING OF PRODUCTION SITES AND THEIR INPUT/OUTPUTS
    production_sites = {}
    all_ps = ProductionSite.objects.all()
    all_ps_inputs = ProductionSiteInput.objects.values("production_site_id", "matiere_premiere_id")
    all_ps_outputs = ProductionSiteOutput.objects.values("production_site_id", "biocarburant_id")

    feedstock_by_ps = {}
    for input in all_ps_inputs:
        production_site_id = input["production_site_id"]
        matiere_premiere_id = input["matiere_premiere_id"]
        if production_site_id not in feedstock_by_ps:
            feedstock_by_ps[production_site_id] = []
        feedstock_by_ps[production_site_id].append(matiere_premiere_id)

    biofuel_by_ps = {}
    for output in all_ps_outputs:
        production_site_id = output["production_site_id"]
        biocarburant_id = output["biocarburant_id"]
        if production_site_id not in biofuel_by_ps:
            biofuel_by_ps[production_site_id] = []
        biofuel_by_ps[production_site_id].append(biocarburant_id)

    for psite in list(all_ps):
        production_sites[psite.pk] = {}
        # [mp['matiere_premiere_id'] for mp in psite.productionsiteinput_set.all().values('matiere_premiere_id')]
        production_sites[psite.pk]["feedstock_ids"] = feedstock_by_ps.get(psite.pk, [])
        # [bc['biocarburant_id'] for bc in psite.productionsiteoutput_set.all().values('biocarburant_id')]
        production_sites[psite.pk]["biofuel_ids"] = biofuel_by_ps.get(psite.pk, [])
    data["production_sites"] = production_sites

    # CLIENTS
    client_entities = list(Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER]))
    data["clients"] = {c.pk: c for c in client_entities}
    data["clientsbyname"] = {c.name.upper(): c for c in client_entities}

    # CERTIFICATES
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    certs = GenericCertificate.objects.filter(valid_until__gte=lastyear).values("certificate_id", "valid_until")
    data["certificates"] = {c["certificate_id"].upper(): c for c in certs}

    dc_certs = DoubleCountingRegistration.objects.all()
    for cert in dc_certs:
        dc_cert = cert.certificate_id
        if cert.production_site:
            dc_cert = f"{dc_cert}_{cert.production_site.pk}"
        data["double_counting_certificates"][dc_cert] = cert

    # ML STATS
    etds = ETDStats.objects.select_related("feedstock").all()
    data["etd"] = {s.feedstock: s.default_value for s in etds}

    eecs = EECStats.objects.select_related("feedstock", "origin").all()
    data["eec"] = {s.feedstock.code + s.origin.code_pays: s for s in eecs}

    eps = EPStats.objects.select_related("feedstock", "biofuel").all()
    data["ep"] = {s.feedstock.code + s.biofuel.code: s for s in eps}

    # used as cache in CarbureLot model - recalc reliability score
    data["checked_certificates"] = {}

    return data
