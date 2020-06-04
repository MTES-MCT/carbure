import os
import django
import xlsxwriter
import datetime
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import MatierePremiere, Biocarburant, Pays, Depot, Entity, ProductionSite


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
               'pays_origine_code', 'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'e', 'dae',
               'client_id', 'ea_delivery_date', 'ea_name', 'ea_delivery_site']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%d/%m/%Y')
    for i in range(10):
        p = random.choice(psites)
        mp = random.choice(mps)
        ea = random.choice(eas)
        bc = random.choice(bcs)
        country = random.choice(countries)
        site = random.choice(delivery_sites)
        volume = random.choice(volumes)

        row = [p.name, volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 0,
               'FR000000123', clientid, today, ea.name, site.depot_id]
        colid = 0
        for elem in row:
            worksheet_lots.write(i+1, colid, elem)
            colid += 1


def make_lots_sheet_v2(workbook, entity):
    worksheet_lots = workbook.add_worksheet("lots")
    psites = ProductionSite.objects.filter(producer=entity)
    eas = Entity.objects.filter(entity_type='Opérateur')
    mps = MatierePremiere.objects.all()
    bcs = Biocarburant.objects.all()
    delivery_sites = Depot.objects.all()
    countries = Pays.objects.all()

    # 3/10 chances of having an imported lot
    imported_lots = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    exported_lots = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    foreign_producers = [{'name': 'ITANOL', 'country': 'IT', 'production_site': 'BERGAMO'},
                         {'name': 'ITANOL', 'country': 'IT', 'production_site': 'FIRENZE'},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'LISBOA'},
                         {'name': 'PORTUGASOIL', 'country': 'PT', 'production_site': 'PORTO'},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'EL MASNOU'},
                         {'name': 'BIOCATALAN', 'country': 'ES', 'production_site': 'EL MASNOU'},
                         {'name': 'BIOBAO', 'country': 'ES', 'production_site': 'HONDARRIBIA'},
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
    columns = ['producer', 'production_site', 'production_site_country',
               'volume', 'biocarburant_code', 'matiere_premiere_code', 'pays_origine_code',
               'eec', 'el', 'ep', 'etd', 'eu', 'esca', 'eccs', 'eccr', 'eee', 'e',
               'dae', 'champ_libre', 'client', 'delivery_date', 'delivery_site', 'delivery_site_country']
    for i, c in enumerate(columns):
        worksheet_lots.write(0, i, c, bold)

    volumes = [1200, 2800, 8000, 4500, 13000]
    clientid = 'import_batch_%s' % (datetime.date.today().strftime('%Y%m%d'))
    today = datetime.date.today().strftime('%d/%m/%Y')
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
            p = random.choice(foreign_producers)
            row += [p['name'], p['production_site'], p['country']]
        else:
            p = random.choice(psites)
            row += ['', p.name, p.country.code_pays]
        row += [volume, bc.code, mp.code, country.code_pays, 12, 4, 2, 0, 3.3, 0, 0, 0, 0, 0, 'FR000000123', clientid]
        if exported:
            c = random.choice(foreign_clients)
            row += [c['name'], today, c['delivery_site'], c['country']]
        else:
            row += [ea.name, today, site.depot_id, 'FR']

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
    worksheet_operateurs = workbook.add_worksheet("OperateursPetroliers")
    operators = Entity.objects.filter(entity_type='Opérateur')
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


def create_template_xlsx_v2(entity):
    # Create an new Excel file and add a worksheet.
    location = '/tmp/carbure_template.xlsx'
    workbook = xlsxwriter.Workbook(location)
    make_lots_sheet_v2(workbook, entity)
    make_mps_sheet(workbook)
    make_biofuels_sheet(workbook)
    make_countries_sheet(workbook)
    make_operators_sheet(workbook)
    make_deliverysites_sheet(workbook)
    workbook.close()
    return location


def main():
    entity = Entity.objects.get(name="Bio Raffinerie Lambda")
    create_template_xlsx(entity)


if __name__ == "__main__":
    main()
