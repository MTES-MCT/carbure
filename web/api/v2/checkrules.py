import datetime
from core.models import LotValidationError, MatierePremiere, Biocarburant, Pays

# init data cache
#MPS = {m.code: m for m in MatierePremiere.objects.all()}
#BCS = {b.code: b for b in Biocarburant.objects.all()}
#COUNTRIES = {p.code_pays: p for p in Pays.objects.all()}

# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)

rules = {}
rules['GHG_REDUC_INF_50'] = "La réduction de gaz à effet de serre est inférieure à 50%, il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['PROVENANCE_MP'] = "Êtes vous sûr de la provenance de votre matière première ?"
rules['MP_BC_INCOHERENT'] = "Matière Première incohérente avec le Biocarburant"
rules['GHG_REDUC_INF_60'] = "La réduction de gaz à effet de serre est inférieure à 60% pour une usine dont la date de mise en service est ultérieure au 5 Octobre 2015. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_INF_65'] = "La réduction de gaz à effet de serre est inférieure à 65% pour une usine dont la date de mise en service est ultérieure au 1er Janvier 2021. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"


def raise_error(lot, rule_triggered, warning_to_user=True, warning_to_admin=False, block_validation=False):
    d = {'warning_to_user': warning_to_user,
         'warning_to_admin': warning_to_admin,
         'block_validation': block_validation,
         'message': rules[rule_triggered]
         }
    LotValidationError.objects.update_or_create(lot=lot, rule_triggered=rule_triggered, defaults=d)


def sanity_check(lot):
    # réduction de GES
    if lot.ghg_reduction < 50:
        raise_error(lot, 'GHG_REDUC_INF_50', warning_to_user=True, block_validation=True)
    commissioning_date = lot.carbure_production_site.date_mise_en_service if lot.carbure_production_site else lot.unknown_production_site_com_date
    if commissioning_date:
        if commissioning_date > oct2015 and lot.ghg_reduction < 60:
            raise_error(lot, 'GHG_REDUC_INF_60', warning_to_user=True, block_validation=True)
        if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
            raise_error(lot, 'GHG_REDUC_INF_65', warning_to_user=True, block_validation=True)

    if lot.matiere_premiere and lot.biocarburant:
        # provenance des matieres premieres
        if lot.matiere_premiere.code == 'SOJA':
            # TODO: remplacer par une liste de pays "douteux" ou a l'inverse utiliser une whitelist et lever une alerte si le pays n'est pas dedans
            if lot.pays_origine.code_pays == 'SE':
                raise_error(lot, 'PROVENANCE_MP', warning_to_user=True, warning_to_admin=True, block_validation=False)

        # consistence des matieres premieres avec biocarburant
        if lot.biocarburant.is_alcool and lot.matiere_premiere.compatible_alcool is False:
            raise_error(lot, 'MP_BC_INCOHERENT', warning_to_user=True, warning_to_admin=True)


        if lot.biocarburant.is_graisse and lot.matiere_premiere.compatible_graisse is False:
            raise_error(lot, 'MP_BC_INCOHERENT', warning_to_user=True, warning_to_admin=True)

        if lot.biocarburant.code in ['EMHV', 'EMHU', 'EMHA', 'HVOG', 'HVOE', 'HOE', 'HOG']:
            if lot.matiere_premiere.code in ['BETTERAVE', 'MAIS', 'BLE', 'ORGE', 'EP2', 'RESIDUS_DE_BIERE', 'TRITICALE', 'SEIGLE', 'AMIDON_RESIDUEL',
                                            'MAT_LIGNO_CELLULOSIQUE', 'MAT_CELLULOSIQUE_NON_ALIMENTAIRE', 'BAGASSE', 'COQUES', 'PAILLE', 'DECHETS_BOIS',
                                            'GLYCERINE_BRUTE', 'RESIDUS_VINIQUES', 'CANNE_A_SUCRE']:
                raise_error(lot, 'MP_BC_INCOHERENT', warning_to_user=True, block_validation=True)

        if lot.biocarburant.code in ['ET', 'ETBE', 'MTBE']:
            if lot.matiere_premiere.code in ['BRAI_TALLOL', 'POME', 'SOJA', 'TOURNESOL', 'COLZA', 'PALME', 'UCO', 'C1', 'C2', 'C3']:
                raise_error(lot, 'MP_BC_INCOHERENT', warning_to_user=True, block_validation=True)
