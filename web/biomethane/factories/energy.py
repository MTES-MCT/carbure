import random

import factory
from faker import Faker

from biomethane.models.biomethane_energy import BiomethaneEnergy
from biomethane.models.biomethane_energy_monthly_report import BiomethaneEnergyMonthlyReport
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity
from entity.factories.entity import EntityFactory

faker = Faker()


class BiomethaneEnergyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneEnergy

    producer = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    year = faker.random_int(2000, 2024)

    # Biométhane injecté dans le réseau
    injected_biomethane_gwh_pcs_per_year = factory.Faker("pyfloat", min_value=0, max_value=1000, right_digits=2)
    injected_biomethane_nm3_per_year = factory.Faker("pyfloat", min_value=0, max_value=100000, right_digits=2)
    injected_biomethane_ch4_rate_percent = factory.Faker("pyfloat", min_value=90, max_value=100, right_digits=1)
    injected_biomethane_pcs_kwh_per_nm3 = factory.Faker("pyfloat", min_value=9, max_value=12, right_digits=2)
    operating_hours = factory.Faker("pyfloat", min_value=0, max_value=8760, right_digits=1)

    # Production de biogaz
    produced_biogas_nm3_per_year = factory.Faker("pyfloat", min_value=0, max_value=150000, right_digits=2)
    flared_biogas_nm3_per_year = factory.Faker("pyfloat", min_value=0, max_value=50000, right_digits=2)
    flaring_operating_hours = factory.Faker("pyfloat", min_value=0, max_value=8760, right_digits=1)

    # Nature de l'énergie utilisée
    attest_no_fossil_for_energy = factory.Faker("boolean")
    energy_types = factory.LazyAttribute(
        lambda obj: random.sample([choice[0] for choice in BiomethaneEnergy.ENERGY_TYPES], k=random.randint(1, 3))
    )
    energy_details = factory.LazyAttribute(lambda obj: faker.text(max_nb_chars=500) if obj.energy_types else None)

    # Efficacité énergétique
    purified_biogas_quantity_nm3 = factory.Faker("pyfloat", min_value=0, max_value=100000, right_digits=2)
    purification_electric_consumption_kwe = factory.Faker("pyfloat", min_value=0, max_value=1000, right_digits=2)
    self_consumed_biogas_nm3 = factory.Faker("pyfloat", min_value=0, max_value=20000, right_digits=2)
    total_unit_electric_consumption_kwe = factory.Faker("pyfloat", min_value=0, max_value=2000, right_digits=2)
    butane_or_propane_addition = factory.Faker("boolean")
    fossil_fuel_consumed_kwh = factory.Faker("pyfloat", min_value=0, max_value=50000, right_digits=2)

    # Questions diverses
    has_opposition_or_complaints_acceptability = factory.Faker("boolean")
    estimated_work_days_acceptability = factory.Faker("random_int", min=0, max=365)

    # Dysfonctionnements
    has_malfunctions = factory.Faker("boolean")
    malfunction_cumulative_duration_days = factory.LazyAttribute(
        lambda obj: faker.random_int(min=1, max=365) if obj.has_malfunctions else None
    )
    malfunction_types = factory.LazyAttribute(
        lambda obj: random.sample([choice[0] for choice in BiomethaneEnergy.MALFUNCTION_TYPES], k=random.randint(1, 3))
        if obj.has_malfunctions
        else None
    )
    malfunction_details = factory.LazyAttribute(
        lambda obj: faker.text(max_nb_chars=500)
        if obj.has_malfunctions and BiomethaneEnergy.MALFUNCTION_TYPE_OTHER in (obj.malfunction_types or [])
        else None
    )

    has_injection_difficulties_due_to_network_saturation = factory.Faker("boolean")
    injection_impossibility_hours = factory.LazyAttribute(
        lambda obj: faker.random_int(min=1, max=8760) if obj.has_injection_difficulties_due_to_network_saturation else None
    )


class BiomethaneEnergyMonthlyReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneEnergyMonthlyReport

    energy = factory.SubFactory(BiomethaneEnergyFactory)
    month = faker.random_int(1, 12)
    injected_volume_nm3 = factory.Faker("pyfloat", min_value=0, max_value=50000, right_digits=2)
    average_monthly_flow_nm3_per_hour = factory.Faker("pyfloat", min_value=0, max_value=1000, right_digits=2)


def create_monthly_reports_for_energy(energy):
    months = range(1, 13)

    reports = []
    for month in months:
        report = BiomethaneEnergyMonthlyReportFactory.create(energy=energy, month=month)
        reports.append(report)

    return reports


def create_biomethane_energy(producer=None, **kwargs):
    if producer is None:
        producer = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
    year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
    previous_year = year - 1

    # Create energy declaration for the current year and the previous year
    energy1 = BiomethaneEnergyFactory.create(producer=producer, year=year, **kwargs)
    create_monthly_reports_for_energy(energy1)

    energy2 = BiomethaneEnergyFactory.create(producer=producer, year=previous_year, **kwargs)
    create_monthly_reports_for_energy(energy2)
