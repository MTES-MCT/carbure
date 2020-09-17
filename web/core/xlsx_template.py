import os
import django
import xlsxwriter
import datetime
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import MatierePremiere, Biocarburant, Pays, Depot, Entity, ProductionSite, LotTransaction


def make_lots_sheet(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    psites = ProductionSite.objects.filter(producer=entity)
    eas = Entity.objects.filter(entity_type='Opérateur')
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['production_site_name', 'volume', 'biocarburant_code', 'matiere_premiere_code',
               'pays_origine_code', 'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'dae',
               'client_id', 'ea_delivery_date', 'ea_name', 'ea_delivery_site']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')

    if not len(psites):
        return

    for i in range(10):
        p = random.choice(psites)
        mp = random.choice(mps)
        ea = random.choice(eas)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)

        row = [p.name, volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0,
               'FR000000123', clientid, today, ea.name, site.depot_id]
        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_lots_sheet_v2_advanced(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    psites = ProductionSite.objects.filter(producer=entity)
    eas = Entity.objects.filter(entity_type__in=['Opérateur', 'Producteur']).exclude(id=entity.id)
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # 3/10 chances of having an imported lot
    imported_lots = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    exported_lots = [1, 1, 1, 0, 0, 0, 0, -1, -1, -1]
    unknown_producers = [{'name': 'ITANOL', 'country': 'IT', 'production_site': 'BERGAMO', 'ref': 'ISCC-IT-100001010', 'date':'2017-12-01', 'dc':'IT_001_2020'},
                         {'name': 'ITANOL', 'country': 'IT', 'production_site': 'FIRENZE', 'ref': 'ISCC-IT-100001011', 'date':'2014-03-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'LISBOA', 'ref': 'ISCC-PT-100001110', 'date':'2011-10-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'PORTO', 'ref': 'ISCC-PT-100001080', 'date':'2013-07-01', 'dc':''},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'EL MASNOU', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'TARRAGONA', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': 'BIOBAO', 'country': 'ES', 'production_site': 'HONDARRIBIA', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'TOURS', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'NUEIL LES AUBIERS', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'BRUZAC', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'NIMES', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         ]

    foreign_clients = [{'name': 'BP', 'country': 'GB', 'delivery_site': 'DOVER'},
                       {'name': 'BP', 'country': 'GB', 'delivery_site': 'LIVERPOOL'},
                       {'name': 'BP', 'country': 'GB', 'delivery_site': 'MANCHESTER'},
                       {'name': 'EXXON', 'country': 'US', 'delivery_site': 'BOSTON'},
                       {'name': 'EXXON', 'country': 'US', 'delivery_site': 'HOBOKEN'},
                       {'name': 'IBERDROLA', 'country': 'ES', 'delivery_site': 'BCN'},
                       {'name': 'IBERDROLA', 'country': 'ES', 'delivery_site': 'BILBAO'},
                       ]

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['producer', 'production_site', 'production_site_country', 'production_site_reference',
               'production_site_commissioning_date', 'double_counting_registration',
               'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
               'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country']
    if entity.producer_with_mac:
        columns.append('mac')
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000, 35000, 34960, 27854, 18000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')
    for i in range(10):
        mp = random.choice(mps)
        ea = random.choice(eas)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)
        imported = random.choice(imported_lots)
        exported = random.choice(exported_lots)

        row = []
        if imported:
            p = random.choice(unknown_producers)
            row += [p['name'], p['production_site'], p['country'], p['ref'], p['date'], p['dc']]
        else:
            if not len(psites):
                continue
            p = random.choice(psites)
            row += [p.producer.name, p.name, p.country.code_pays, '', '', '']
        row += [volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 'FR000000123', clientid]
        if exported == 1:
            # client is not in carbure
            c = random.choice(foreign_clients)
            row += [c['name'], today, c['delivery_site'], c['country']]
        elif exported == -1:
            # into mass balance (i am the client)
            row += ['', today, site.depot_id, 'FR']
        else:
            # regular transaction. sell to someone else
            row += [ea.name, today, site.depot_id, 'FR']

        if entity.producer_with_mac:
            row += [0]

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_mb_extract_sheet(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    clients = Entity.objects.filter(entity_type__in=['Opérateur', 'Producteur', 'Trader']).exclude(id=entity.id)
    delivery_sites = Depot.objects.all()
    mb_lots = LotTransaction.objects.filter(carbure_client=entity, delivery_status='A', lot__status="Validated", lot__fused_with=None)

    # 4/10 chances of having an exported lot
    exported_lots = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
    foreign_clients = [{'name': 'BP', 'country': 'GB', 'delivery_site': 'DOVER'},
                       {'name': 'BP', 'country': 'GB', 'delivery_site': 'LIVERPOOL'},
                       {'name': 'BP', 'country': 'GB', 'delivery_site': 'MANCHESTER'},
                       {'name': 'EXXON', 'country': 'US', 'delivery_site': 'BOSTON'},
                       {'name': 'EXXON', 'country': 'US', 'delivery_site': 'HOBOKEN'},
                       {'name': 'IBERDROLA', 'country': 'ES', 'delivery_site': 'BCN'},
                       {'name': 'IBERDROLA', 'country': 'ES', 'delivery_site': 'BILBAO'},
                       ]

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['carbure_id', 'volume', 'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')
    for i in range(10):
        client = random.choice(clients)
        site = random.choice(delivery_sites)
        exported = random.choice(exported_lots)
        lot_source = random.choice(mb_lots)

        row = [lot_source.lot.carbure_id, int(lot_source.lot.volume / 2), 'FR000000123', clientid]
        if exported == 1:
            # client is not in carbure
            c = random.choice(foreign_clients)
            row += [c['name'], today, c['delivery_site'], c['country']]
        else:
            # regular transaction. sell to someone else
            row += [client.name, today, site.depot_id, '']

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_lots_sheet_v2_simple(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    psites = ProductionSite.objects.filter(producer=entity)
    eas = Entity.objects.filter(entity_type__in=['Opérateur', 'Trader'])
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['production_site', 'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
               'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')

    if not len(psites):
        return

    for i in range(10):
        mp = random.choice(mps)
        ea = random.choice(eas)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)

        p = random.choice(psites)
        row = [p.name, volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 'FR000000123', clientid]
        row += [ea.name, today, site.depot_id]

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_traders_lots_sheet(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()
    eas = Entity.objects.filter(entity_type__in=['Opérateur', 'Trader'])

    # 3/10 chances of having an imported lot
    unknown_producers = [{'name': 'ITANOL', 'country': 'IT', 'production_site': 'BERGAMO', 'ref': 'ISCC-IT-100001010', 'date':'2017-12-01', 'dc':'IT_001_2020'},
                         {'name': 'ITANOL', 'country': 'IT', 'production_site': 'FIRENZE', 'ref': 'ISCC-IT-100001011', 'date':'2014-03-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'LISBOA', 'ref': 'ISCC-PT-100001110', 'date':'2011-10-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'PORTO', 'ref': 'ISCC-PT-100001080', 'date':'2013-07-01', 'dc':''},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'EL MASNOU', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'TARRAGONA', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': 'BIOBAO', 'country': 'ES', 'production_site': 'HONDARRIBIA', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'TOURS', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'NUEIL LES AUBIERS', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'BRUZAC', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'NIMES', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         ]

    vendors = ['LUR BERRI', 'ITANOL', 'FINNHUB', 'DEUTSCHE BIOFUELS GMBH', 'SUCRERIE HARIBO', '', '', '', '', '']

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['producer', 'production_site', 'production_site_country', 'production_site_reference',
               'production_site_commissioning_date', 'double_counting_registration',
               'vendor', 'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
               'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000, 35000, 34960, 27854, 18000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')
    for i in range(10):
        mp = random.choice(mps)
        vendor = random.choice(vendors)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)
        ea = None
        if i % 3 == 1:
            ea = random.choice(eas)

        row = []
        p = random.choice(unknown_producers)
        row += [p['name'], p['production_site'], p['country'], p['ref'], p['date'], p['dc']]
        row += [vendor, volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 'FR000000123', clientid]
        row += [ea.name if ea else '', today, site.depot_id, 'FR']

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_operators_lots_sheet(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # 3/10 chances of having an imported lot
    unknown_producers = [{'name': 'ITANOL', 'country': 'IT', 'production_site': 'BERGAMO', 'ref': 'ISCC-IT-100001010', 'date':'2017-12-01', 'dc':'IT_001_2020'},
                         {'name': 'ITANOL', 'country': 'IT', 'production_site': 'FIRENZE', 'ref': 'ISCC-IT-100001011', 'date':'2014-03-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'LISBOA', 'ref': 'ISCC-PT-100001110', 'date':'2011-10-01', 'dc':''},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'PORTO', 'ref': 'ISCC-PT-100001080', 'date':'2013-07-01', 'dc':''},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'EL MASNOU', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'TARRAGONA', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': 'BIOBAO', 'country': 'ES', 'production_site': 'HONDARRIBIA', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'TOURS', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': 'BONDUELLE', 'country': 'FR', 'production_site': 'NUEIL LES AUBIERS', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'BRUZAC', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': 'GEANTVERT', 'country': 'FR', 'production_site': 'NIMES', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100002010', 'date':'2016-02-01', 'dc':'ES_012_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100005010', 'date':'2019-12-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-ES-100004010', 'date':'2007-11-01', 'dc':'ES_011_2018'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001011', 'date':'2001-01-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001012', 'date':'2004-06-01', 'dc':'FR_042_2016'},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001013', 'date':'2005-04-01', 'dc':''},
                         {'name': '', 'country': '', 'production_site': '', 'ref': 'ISCC-FR-100001014', 'date':'1997-07-01', 'dc':'FR_002_2017'},
                         ]

    vendors = ['LUR BERRI', 'ITANOL', 'FINNHUB', 'DEUTSCHE BIOFUELS GMBH', 'SUCRERIE HARIBO', '', '', '', '', '']

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['producer', 'production_site', 'production_site_country', 'production_site_reference',
               'production_site_commissioning_date', 'double_counting_registration',
               'vendor', 'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
               'dae', 'champ_libre', 'delivery_date', 'delivery_site']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000, 35000, 34960, 27854, 18000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%Y-%m-%d')
    for i in range(10):
        mp = random.choice(mps)
        vendor = random.choice(vendors)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)
        row = []
        p = random.choice(unknown_producers)
        row += [p['name'], p['production_site'], p['country'], p['ref'], p['date'], p['dc']]
        row += [vendor, volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 'FR000000123', clientid]
        row += [today, site.depot_id]

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_mps_sheet(workbook):
    worksheet_mps = workbook.add_worksheet("MatieresPremieres")
    mps = MatierePremiere.objects.all()
    # header
    bold = workbook.add_format({'bold': True})
    worksheet_mps.write('A1', 'code', bold)
    worksheet_mps.write('B1', 'name', bold)
    # content
    row = 1
    for m in mps:
        worksheet_mps.write(row, 0, m.code)
        worksheet_mps.write(row, 1, m.name)
        row += 1


def make_biofuels_sheet(workbook):
    worksheet_biocarburants = workbook.add_worksheet("Biocarburants")
    biocarburants = Biocarburant.objects.all()
    # header
    bold = workbook.add_format({'bold': True})
    worksheet_biocarburants.write('A1', 'code', bold)
    worksheet_biocarburants.write('B1', 'name', bold)
    # content
    row = 1
    for b in biocarburants:
        worksheet_biocarburants.write(row, 0, b.code)
        worksheet_biocarburants.write(row, 1, b.name)
        row += 1


def make_countries_sheet(workbook):
    worksheet_pays = workbook.add_worksheet("Pays")
    pays = Pays.objects.all()
    # header
    bold = workbook.add_format({'bold': True})
    worksheet_pays.write('A1', 'code', bold)
    worksheet_pays.write('B1', 'name', bold)
    # content
    row = 1
    for p in pays:
        worksheet_pays.write(row, 0, p.code_pays)
        worksheet_pays.write(row, 1, p.name)
        row += 1


def make_operators_sheet(workbook):
    worksheet_operateurs = workbook.add_worksheet("Societes")
    operators = Entity.objects.filter(entity_type__in=['Opérateur', 'Producteur', 'Trader'])
    # header
    bold = workbook.add_format({'bold': True})
    worksheet_operateurs.write('A1', 'name', bold)
    # content
    row = 1
    for o in operators:
        worksheet_operateurs.write(row, 0, o.name)
        row += 1


def make_deliverysites_sheet(workbook):
    worksheet_sites = workbook.add_worksheet("SitesDeLivraison")
    depots = Depot.objects.all()
    # header
    bold = workbook.add_format({'bold': True})
    worksheet_sites.write('A1', 'code', bold)
    worksheet_sites.write('B1', 'name', bold)
    worksheet_sites.write('C1', 'city', bold)
    # content
    row = 1
    for d in depots:
        worksheet_sites.write(row, 0, d.depot_id)
        worksheet_sites.write(row, 1, d.name)
        worksheet_sites.write(row, 2, d.city)
        row += 1


def create_template_xlsx(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_lots_sheet(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


def create_template_xlsx_v2_simple(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template_simple.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_lots_sheet_v2_simple(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


def create_template_xlsx_v2_advanced(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template_advanced.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_lots_sheet_v2_advanced(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


def create_template_xlsx_v2_operators(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template_operators.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_operators_lots_sheet(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    workbook.close()
    return location


def create_template_xlsx_v2_traders(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template_traders.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_traders_lots_sheet(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    workbook.close()
    return location


def create_template_xlsx_v2_mb(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template_mb.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_mb_extract_sheet(workbook, entity)
    make_countries_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


# API V3
def make_dump_lots_sheet(workbook, entity, transactions):
    worksheet_lots = workbook.add_worksheet("lots")
    psites = ProductionSite.objects.filter(producer=entity)
    eas = Entity.objects.filter(entity_type__in=['Opérateur', 'Producteur', 'Trader']).exclude(id=entity.id)
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # header
    bold = workbook.add_format({'bold': True})
    columns = ['carbure_id', 'producer', 'production_site', 'production_site_country', 'production_site_reference',
               'production_site_commissioning_date', 'double_counting_registration',
               'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee',
               'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country']
    if entity.producer_with_mac:
        columns.append('mac')
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    for tx in transactions:
        lot = tx.lot
        row = [lot.carbure_id,
               lot.carbure_producer.name if lot.carbure_producer else lot.unknown_producer,
               lot.carbure_production_site.name if lot.carbure_production_site else lot.unknown_production_site,
               lot.carbure_production_site.country.code_pays if lot.carbure_production_site and lot.carbure_production_site.country else lot.unknown_production_country.code_pays if lot.unknown_production_country else '',
               lot.unknown_production_site_reference, lot.unknown_production_site_com_date, lot.unknown_production_site_dbl_counting,
               lot.volume, lot.biocarburant.code if lot.biocarburant else '',
               lot.matiere_premiere.code if lot.matiere_premiere else '',
               lot.pays_origine.code_pays if lot.pays_origine else '',
               lot.eec, lot.el, lot.ep, lot.etd, lot.eu, lot.esca, lot.eccs, lot.eccr, lot.eee, lot.ghg_total,
               tx.dae, tx.champ_libre, tx.carbure_client.name if tx.client_is_in_carbure else tx.unknown_client, tx.delivery_date,
               tx.carbure_delivery_site.depot_id if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site,
               tx.carbure_delivery_site.country.code_pays if tx.delivery_site_is_in_carbure else tx.unknown_delivery_site_country.code_pays if tx.unknown_delivery_site_country else ''
               ]
        if entity.producer_with_mac:
            row += [tx.is_mac]

        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def create_xslx_from_transactions(entity, transactions):
    today = datetime.date.today()
    location = '/tmp/carbure_export_%s.xlsx' % (today.strftime('%Y%m%d_%H%M'))
    workbook = xlsxwriter.Workbook(location)
    make_dump_lots_sheet(workbook, entity, transactions)
    make_countries_sheet(workbook)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


def main():
    entity = Entity.objects.get(name="Bio Raffinerie Lambda")
    create_template_xlsx(entity)


if __name__ == "__main__":
    main()
