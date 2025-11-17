"""
Service d'anonymisation des données sensibles pour les environnements de développement.

Utilise bulk_update() et traitement par batch pour optimiser les performances
sur de grandes quantités de données.
"""

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import transaction
from faker import Faker

from biomethane.models import (
    BiomethaneContract,
    BiomethaneContractAmendment,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
)
from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureLotEvent,
    CarbureNotification,
    CarbureStockEvent,
    Depot,
    Entity,
    GenericCertificate,
)
from doublecount.models import DoubleCountingApplication, DoubleCountingDocFile, DoubleCountingSourcingHistory
from elec.models import (
    ElecChargePoint,
    ElecMeter,
    ElecProvisionCertificate,
    ElecProvisionCertificateQualicharge,
    ElecTransferCertificate,
)
from producers.models import ProductionSite
from saf.models import SafTicket, SafTicketSource
from transactions.models import Site

User = get_user_model()

# Taille des batches pour le traitement par lots
BATCH_SIZE = 2000


class DataAnonymizationService:
    """
    Service pour anonymiser les données sensibles de la base de données.

    Utilise bulk_update() pour optimiser les performances sur de grandes
    quantités de données.
    """

    def __init__(self, batch_size=BATCH_SIZE):
        self.fake = Faker("fr_FR")
        self.batch_size = batch_size

        # Mapping pour cohérence (optionnel, pour maintenir des relations)
        self.entity_names = {}
        self.user_emails = {}

    def _process_in_batches(self, queryset, process_func, model_name):
        """
        Traite un queryset par batch pour éviter de charger trop de données en mémoire.

        Args:
            queryset: QuerySet à traiter
            process_func: Fonction qui prend un batch d'objets et retourne les objets modifiés
            model_name: Nom du modèle pour les logs
        """
        total = queryset.count()
        if total == 0:
            print(f"   → {model_name}: Aucun enregistrement à traiter")
            return 0

        print(f"   → {model_name}: {total} enregistrements à traiter...")

        paginator = Paginator(queryset, self.batch_size)
        total_processed = 0

        for page_num in paginator.page_range:
            page = paginator.page(page_num)
            batch = list(page.object_list)

            # Traiter le batch
            updated_objects = process_func(batch)

            # Sauvegarder en bulk
            if updated_objects:
                # Déterminer les champs à mettre à jour
                update_fields = list(updated_objects[0].__dict__.keys())
                # Retirer les champs Django internes
                update_fields = [f for f in update_fields if not f.startswith("_") and f != "id"]

                # Utiliser bulk_update
                type(updated_objects[0]).objects.bulk_update(updated_objects, update_fields, batch_size=self.batch_size)

            total_processed += len(updated_objects)

            print(f"      Traité: {total_processed}/{total}", end="\r")

        print(f"   → {model_name}: {total_processed} enregistrements traités")
        return total_processed

    @transaction.atomic
    def anonymize_all(self):
        """Anonymise tous les modèles dans l'ordre correct"""

        # Ordre d'exécution
        self.anonymize_users()
        self.anonymize_entities()
        self.anonymize_sites()
        self.anonymize_depots()
        self.anonymize_production_sites()
        self.anonymize_biomethane_models()
        self.anonymize_double_counting()
        self.anonymize_elec_models()
        self.anonymize_saf_models()
        self.anonymize_carbure_lots()
        self.anonymize_certificates()
        self.anonymize_carbure_lot_comments()
        self.empty_history_tables()

        print("\n✅ Anonymisation terminée avec succès")

    # ========== MODÈLES PRINCIPAUX ==========

    def anonymize_users(self):
        """Anonymise authtools_user avec bulk_update"""
        print("📝 Anonymisation des utilisateurs...")

        def process_batch(batch):
            updated = []
            for user in batch:
                user.email = f"user{user.id}@anonymized.local"
                user.name = f"Utilisateur {user.id}"
                self.user_emails[user.id] = user.email
                updated.append(user)
            return updated

        self._process_in_batches(User.objects.all(), process_batch, "Users")

    def anonymize_entities(self):
        """Anonymise entities avec bulk_update"""
        print("🏢 Anonymisation des entités...")

        def process_batch(batch):
            updated = []
            for entity in batch:
                # Nom basé sur le type
                entity.name = f"{entity.entity_type} - Entreprise {entity.id}"
                entity.legal_name = f"{entity.name} SA"

                # Contact
                entity.sustainability_officer = self.fake.name()
                entity.sustainability_officer_email = f"contact{entity.id}@anonymized.local"
                entity.sustainability_officer_phone_number = self.fake.phone_number()

                # Adresse
                entity.registered_address = self.fake.address()
                entity.registered_city = self.fake.city()
                entity.registered_zipcode = self.fake.postcode()

                # Identifiants légaux
                entity.registration_id = self.fake.bothify(text="##########")
                entity.vat_number = self.fake.bothify(text="FR#############")
                entity.accise_number = self.fake.bothify(text="##########")

                # Autres
                entity.website = self.fake.url()
                entity.activity_description = self.fake.text(max_nb_chars=200)

                self.entity_names[entity.id] = entity.name
                updated.append(entity)
            return updated

        self._process_in_batches(Entity.objects.all(), process_batch, "Entities")

    def anonymize_production_sites(self):
        """Anonymise producer_sites avec bulk_update"""
        print("🏭 Anonymisation des sites de production...")

        def process_batch(batch):
            updated = []
            for site in batch:
                site.name = f"Site de Production {site.id}"
                site.address = self.fake.address()
                site.city = self.fake.city()
                site.postal_code = self.fake.postcode()
                site.manager_name = self.fake.name()
                site.manager_email = f"manager{site.id}@anonymized.local"
                site.manager_phone = self.fake.phone_number()
                site.site_id = self.fake.bothify(text="SITE-####")
                site.dc_number = self.fake.bothify(text="DC-####")
                site.dc_reference = self.fake.bothify(text="DC-REF-####")
                # GPS en France
                site.gps_coordinates = f"{self.fake.latitude()*5+46}, {self.fake.longitude()*15-5}"
                updated.append(site)
            return updated

        self._process_in_batches(ProductionSite.objects.all(), process_batch, "ProductionSites")

    def anonymize_sites(self):
        """Anonymise sites (transactions.Site) avec bulk_update"""
        print("📍 Anonymisation des sites...")

        def process_batch(batch):
            updated = []
            for site in batch:
                site.name = f"Site {site.site_type} {site.id}"
                site.site_siret = self.fake.bothify(text="##############")
                site.customs_id = self.fake.bothify(text="CUST-####")
                site.address = self.fake.address()
                site.postal_code = self.fake.postcode()
                site.city = self.fake.city()
                site.gps_coordinates = f"{self.fake.latitude()*5+46}, {self.fake.longitude()*15-5}"
                site.dc_number = self.fake.bothify(text="DC-####")
                site.manager_name = self.fake.name()
                site.manager_phone = self.fake.phone_number()
                site.manager_email = f"manager{site.id}@anonymized.local"
                site.icao_code = self.fake.bothify(text="????").upper()
                updated.append(site)
            return updated

        self._process_in_batches(Site.objects.all(), process_batch, "Sites")

    def anonymize_depots(self):
        """Anonymise depots avec bulk_update"""
        print("🏪 Anonymisation des dépôts...")

        def process_batch(batch):
            updated = []
            for depot in batch:
                depot.name = f"Dépôt {depot.depot_type} {depot.id}"
                depot.city = self.fake.city()
                depot.address = self.fake.address()
                depot.postal_code = self.fake.postcode()
                depot.gps_coordinates = f"{self.fake.latitude()*5+46}, {self.fake.longitude()*15-5}"
                updated.append(depot)
            return updated

        self._process_in_batches(Depot.objects.all(), process_batch, "Depots")

    # ========== MODÈLES BIOMÉTHANE ==========

    def anonymize_biomethane_models(self):
        """Anonymise tous les modèles biométhane"""
        self.anonymize_biomethane_contracts()
        self.anonymize_biomethane_contract_amendments()
        self.anonymize_biomethane_injection_sites()
        self.anonymize_biomethane_production_units()

    def anonymize_biomethane_contracts(self):
        """Anonymise biomethane_contract avec bulk_update"""
        print("📄 Anonymisation des contrats biométhane...")

        def process_batch(batch):
            updated = []
            for contract in batch:
                if contract.general_conditions_file:
                    contract.general_conditions_file.name = f"biomethane/contracts/general_{contract.id}.pdf"
                if contract.specific_conditions_file:
                    contract.specific_conditions_file.name = f"biomethane/contracts/specific_{contract.id}.pdf"
                updated.append(contract)
            return updated

        self._process_in_batches(BiomethaneContract.objects.all(), process_batch, "BiomethaneContracts")

    def anonymize_biomethane_contract_amendments(self):
        """Anonymise biomethane_contract_amendment avec bulk_update"""
        print("📝 Anonymisation des amendements de contrats...")

        def process_batch(batch):
            updated = []
            for amendment in batch:
                if amendment.amendment_file:
                    amendment.amendment_file.name = f"biomethane/amendments/amendment_{amendment.id}.pdf"
                amendment.amendment_details = self.fake.text(max_nb_chars=500)
                updated.append(amendment)
            return updated

        self._process_in_batches(BiomethaneContractAmendment.objects.all(), process_batch, "BiomethaneContractAmendments")

    def anonymize_biomethane_injection_sites(self):
        """Anonymise biomethane_injection_site avec bulk_update"""
        print("💉 Anonymisation des sites d'injection...")

        def process_batch(batch):
            updated = []
            for site in batch:
                site.unique_identification_number = self.fake.bothify(text="INJ-####-####")
                site.meter_number = self.fake.bothify(text="METER-####")
                site.company_address = self.fake.address()
                site.city = self.fake.city()
                site.postal_code = self.fake.postcode()
                site.network_manager_name = self.fake.company()
                updated.append(site)
            return updated

        self._process_in_batches(BiomethaneInjectionSite.objects.all(), process_batch, "BiomethaneInjectionSites")

    def anonymize_biomethane_production_units(self):
        """Anonymise biomethane_production_unit avec bulk_update"""
        print("⚙️ Anonymisation des unités de production...")

        def process_batch(batch):
            updated = []
            for unit in batch:
                unit.unit_name = f"Unité de Production {unit.id}"
                unit.siret_number = self.fake.bothify(text="##############")
                unit.company_address = self.fake.address()
                unit.city = self.fake.city()
                unit.postal_code = self.fake.postcode()
                updated.append(unit)
            return updated

        self._process_in_batches(BiomethaneProductionUnit.objects.all(), process_batch, "BiomethaneProductionUnits")

    # ========== MODÈLES DOUBLE COUNTING ==========

    def anonymize_double_counting(self):
        """Anonymise tous les modèles double counting"""
        self.anonymize_double_counting_applications()
        self.anonymize_double_counting_doc_files()
        self.anonymize_double_counting_sourcing_history()

    def anonymize_double_counting_applications(self):
        """Anonymise double_counting_applications avec bulk_update"""
        print("📋 Anonymisation des dossiers double compte...")

        def process_batch(batch):
            updated = []
            for app in batch:
                if app.download_link:
                    app.download_link = f"https://s3.amazonaws.com/bucket/dc/app_{app.id}.pdf"
                updated.append(app)
            return updated

        self._process_in_batches(DoubleCountingApplication.objects.all(), process_batch, "DoubleCountingApplications")

    def anonymize_double_counting_doc_files(self):
        """Anonymise double_counting_doc_files avec bulk_update"""
        print("📎 Anonymisation des fichiers double compte...")

        def process_batch(batch):
            updated = []
            for file in batch:
                file.url = f"https://s3.amazonaws.com/bucket/double-counting/doc_{file.id}.pdf"
                file.file_name = f"document_{file.id}.pdf"
                updated.append(file)
            return updated

        self._process_in_batches(DoubleCountingDocFile.objects.all(), process_batch, "DoubleCountingDocFiles")

    def anonymize_double_counting_sourcing_history(self):
        """Anonymise double_counting_sourcing_history avec bulk_update"""
        print("📊 Anonymisation de l'historique sourcing...")

        def process_batch(batch):
            updated = []
            for item in batch:
                item.raw_material_supplier = self.fake.company()
                item.supplier_certificate_name = self.fake.bothify(text="CERT-####-####")
                updated.append(item)
            return updated

        self._process_in_batches(DoubleCountingSourcingHistory.objects.all(), process_batch, "DoubleCountingSourcingHistory")

    # ========== MODÈLES ELEC ==========

    def anonymize_elec_models(self):
        """Anonymise tous les modèles électricité"""
        self.anonymize_elec_charge_points()
        self.anonymize_elec_meters()
        self.anonymize_elec_transfer_certificates()
        self.anonymize_elec_provision_certificates()

    def anonymize_elec_charge_points(self):
        """Anonymise elec_charge_point avec bulk_update"""
        print("🔌 Anonymisation des points de charge...")

        def process_batch(batch):
            updated = []
            for point in batch:
                point.charge_point_id = self.fake.bothify(text="CP-####-####")
                point.measure_reference_point_id = self.fake.bothify(text="MRP-####")
                point.station_name = f"Station {point.id}"
                point.station_id = self.fake.bothify(text="ST-####")
                point.cpo_name = self.fake.company()
                point.cpo_siren = self.fake.bothify(text="##########")
                # Coordonnées en France
                point.latitude = self.fake.latitude() * 5 + 46
                point.longitude = self.fake.longitude() * 15 - 5
                updated.append(point)
            return updated

        self._process_in_batches(ElecChargePoint.objects.all(), process_batch, "ElecChargePoints")

    def anonymize_elec_meters(self):
        """Anonymise elec_meter avec bulk_update"""
        print("📊 Anonymisation des compteurs électriques...")

        def process_batch(batch):
            updated = []
            for meter in batch:
                meter.mid_certificate = self.fake.bothify(text="MID-CERT-####-####")
                updated.append(meter)
            return updated

        self._process_in_batches(ElecMeter.objects.all(), process_batch, "ElecMeters")

    def anonymize_elec_transfer_certificates(self):
        """Anonymise elec_transfer_certificate avec bulk_update"""
        print("📜 Anonymisation des certificats de transfert...")

        def process_batch(batch):
            updated = []
            for cert in batch:
                cert.certificate_id = self.fake.bothify(text="ETC-####-####")
                updated.append(cert)
            return updated

        self._process_in_batches(ElecTransferCertificate.objects.all(), process_batch, "ElecTransferCertificates")

    def anonymize_elec_provision_certificates(self):
        """Anonymise elec_provision_certificate et qualicharge avec bulk_update"""
        print("⚡ Anonymisation des certificats de provision...")

        # ElecProvisionCertificate
        def process_batch_cert(batch):
            updated = []
            for cert in batch:
                if hasattr(cert, "operation_unit") and cert.operation_unit:
                    cert.operation_unit = self.fake.bothify(text="OP-####")
                updated.append(cert)
            return updated

        self._process_in_batches(ElecProvisionCertificate.objects.all(), process_batch_cert, "ElecProvisionCertificates")

        # ElecProvisionCertificateQualicharge
        def process_batch_qualicharge(batch):
            updated = []
            for cert in batch:
                if hasattr(cert, "operation_unit") and cert.operation_unit:
                    cert.operation_unit = self.fake.bothify(text="OP-####")
                if hasattr(cert, "station_id") and cert.station_id:
                    cert.station_id = self.fake.bothify(text="ST-####")
                updated.append(cert)
            return updated

        self._process_in_batches(
            ElecProvisionCertificateQualicharge.objects.all(),
            process_batch_qualicharge,
            "ElecProvisionCertificateQualicharge",
        )

    # ========== MODÈLES SAF ==========

    def anonymize_saf_models(self):
        """Anonymise tous les modèles SAF"""
        self.anonymize_saf_tickets()
        self.anonymize_saf_ticket_sources()

    def anonymize_saf_tickets(self):
        """Anonymise saf_ticket avec bulk_update"""
        print("✈️ Anonymisation des tickets SAF...")

        def process_batch(batch):
            updated = []
            for ticket in batch:
                if ticket.unknown_producer:
                    ticket.unknown_producer = self.fake.company()
                if ticket.unknown_production_site:
                    ticket.unknown_production_site = f"Site {ticket.id}"
                if ticket.client_comment:
                    ticket.client_comment = self.fake.text(max_nb_chars=200)
                if ticket.free_field:
                    ticket.free_field = self.fake.text(max_nb_chars=500)
                updated.append(ticket)
            return updated

        self._process_in_batches(SafTicket.objects.all(), process_batch, "SafTickets")

    def anonymize_saf_ticket_sources(self):
        """Anonymise saf_ticket_source avec bulk_update"""
        print("📦 Anonymisation des sources de tickets SAF...")

        def process_batch(batch):
            updated = []
            for source in batch:
                if source.unknown_producer:
                    source.unknown_producer = self.fake.company()
                if source.unknown_production_site:
                    source.unknown_production_site = f"Site {source.id}"
                updated.append(source)
            return updated

        self._process_in_batches(SafTicketSource.objects.all(), process_batch, "SafTicketSources")

    # ========== MODÈLES CARBURE ==========

    def anonymize_carbure_lots(self):
        """Anonymise carbure_lots avec bulk_update"""
        print("🛢️ Anonymisation des lots carbure...")

        def process_batch(batch):
            updated = []
            for lot in batch:
                if lot.unknown_producer:
                    lot.unknown_producer = self.fake.company()
                if lot.unknown_production_site:
                    lot.unknown_production_site = f"Site {lot.id}"
                if lot.unknown_supplier:
                    lot.unknown_supplier = self.fake.company()
                if lot.unknown_client:
                    lot.unknown_client = self.fake.company()
                if lot.unknown_dispatch_site:
                    lot.unknown_dispatch_site = f"Site dispatch {lot.id}"
                if lot.unknown_delivery_site:
                    lot.unknown_delivery_site = f"Site delivery {lot.id}"
                # supplier_certificate : garder le format mais anonymiser
                if lot.supplier_certificate:
                    lot.supplier_certificate = self.fake.bothify(text="CERT-####-####")
                updated.append(lot)
            return updated

        self._process_in_batches(CarbureLot.objects.all(), process_batch, "CarbureLots")

    def anonymize_certificates(self):
        """Anonymise carbure_certificates (GenericCertificate) avec bulk_update"""
        print("📜 Anonymisation des certificats...")
        # Anonymiser uniquement les certificats système national
        certs_qs = GenericCertificate.objects.filter(certificate_type="SYSTEME_NATIONAL")

        def process_batch(batch):
            updated = []
            for cert in batch:
                cert.certificate_id = self.fake.bothify(text="SN-CERT-####-####")
                cert.certificate_holder = self.fake.company()
                cert.address = self.fake.address()
                updated.append(cert)
            return updated

        self._process_in_batches(certs_qs, process_batch, "Certificates")

    def anonymize_carbure_lot_comments(self):
        """Anonymise carbure_lots_comments avec bulk_update"""
        print("💬 Anonymisation des commentaires...")

        def process_batch(batch):
            updated = []
            for comment in batch:
                comment.comment = self.fake.text(max_nb_chars=500)
                updated.append(comment)
            return updated

        self._process_in_batches(CarbureLotComment.objects.all(), process_batch, "CarbureLotComments")

    # ========== VIDAGE DES TABLES ==========

    def empty_history_tables(self):
        """Vide les tables d'historique/événements avec delete() optimisé"""
        print("🗑️  Vidage des tables d'historique...")

        tables_to_empty = [
            ("carbure_lots_events", CarbureLotEvent),
            ("carbure_notifications", CarbureNotification),
            ("carbure_stock_events", CarbureStockEvent),
        ]

        for table_name, Model in tables_to_empty:
            try:
                count = Model.objects.count()
                # Utiliser delete() qui est optimisé par Django
                Model.objects.all().delete()
                print(f"   → {table_name}: {count} entrées supprimées")
            except Exception as e:
                print(f"   ⚠️  Erreur pour {table_name}: {e}")

        # Tables avec historique Django (simple_history)
        try:
            from elec.models.elec_charge_point import ElecChargePointHistory

            count = ElecChargePointHistory.objects.count()
            ElecChargePointHistory.objects.all().delete()
            print(f"   → elec_charge_point_history: {count} entrées supprimées")
        except Exception as e:
            print(f"   ⚠️  Erreur pour elec_charge_point_history: {e}")

        try:
            from elec.models.elec_meter import ElecMeterHistory

            count = ElecMeterHistory.objects.count()
            ElecMeterHistory.objects.all().delete()
            print(f"   → elec_meter_history: {count} entrées supprimées")
        except Exception as e:
            print(f"   ⚠️  Erreur pour elec_meter_history: {e}")
