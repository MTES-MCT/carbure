from datetime import date

from django.utils import timezone

from core.factories.sample_data import set_user_access, setup_admin_user, setup_france, setup_regular_user
from core.models import Entity, UserRights
from elec.models import (
    ElecChargePoint,
    ElecChargePointApplication,
    ElecMeter,
    ElecMeterReading,
    ElecMeterReadingApplication,
    ElecProvisionCertificate,
    ElecTransferCertificate,
)
from entity.factories.entity import EntityFactory

OPERATING_UNIT = "FRZZA"
ENR_RATIO = 0.25


def setup_cpo() -> Entity:
    cpo = EntityFactory.create(
        name="CPO Test",
        entity_type=Entity.CPO,
        has_elec=True,
        registered_country=setup_france(),
    )
    set_user_access(setup_admin_user(), cpo, UserRights.ADMIN)
    set_user_access(setup_regular_user(), cpo, UserRights.RW)
    return cpo


def setup_charge_points(cpo: Entity, year: int) -> list[ElecMeter]:
    application, _ = ElecChargePointApplication.objects.get_or_create(cpo=cpo, status=ElecChargePointApplication.ACCEPTED)
    meters = []
    for number in range(1, 5):
        charge_point, _ = ElecChargePoint.objects.get_or_create(
            cpo=cpo,
            charge_point_id=f"{OPERATING_UNIT}E{number:06d}",
            defaults={
                "application": application,
                "current_type": ElecChargePoint.AC,
                "installation_date": date(year - 1, 12, 1),
                "measure_reference_point_id": f"PRM-DEMO-{(number - 1) // 2 + 1:02d}",
                "station_name": f"Station Test {(number - 1) // 2 + 1}",
                "station_id": f"{OPERATING_UNIT}P{(number - 1) // 2 + 1:06d}",
                "nominal_power": 22,
                "cpo_name": cpo.name,
                "cpo_siren": cpo.registration_id,
            },
        )
        meter, _ = ElecMeter.objects.get_or_create(
            charge_point=charge_point,
            mid_certificate=f"MID-DEMO-{number:04d}",
            defaults={"initial_index": 1000, "initial_index_date": date(year - 1, 12, 1)},
        )
        if charge_point.current_meter_id is None:
            charge_point.current_meter = meter
            charge_point.save(update_fields=["current_meter"])
        meters.append(meter)
    return meters


def setup_meter_readings(cpo: Entity, meters: list[ElecMeter], year: int):
    for quarter, reading_date in [(1, date(year, 3, 31)), (2, date(year, 6, 30))]:
        application, _ = ElecMeterReadingApplication.objects.get_or_create(
            cpo=cpo,
            year=year,
            quarter=quarter,
            defaults={"status": ElecMeterReadingApplication.ACCEPTED},
        )
        for number, meter in enumerate(meters, start=1):
            ElecMeterReading.objects.get_or_create(
                application=application,
                meter=meter,
                defaults={
                    "cpo": cpo,
                    "reading_date": reading_date,
                    "extracted_energy": 1000 + quarter * (3000 + number * 250),
                    "enr_ratio": ENR_RATIO,
                    "operating_unit": OPERATING_UNIT,
                },
            )

        # Les certificats sont exprimés en MWh renouvelables, les index en kWh.
        renewable_energy = sum((3000 + number * 250) * ENR_RATIO for number in range(1, len(meters) + 1)) / 1000
        ElecProvisionCertificate.objects.get_or_create(
            cpo=cpo,
            year=year,
            quarter=quarter,
            operating_unit=OPERATING_UNIT,
            source=ElecProvisionCertificate.METER_READINGS,
            defaults={"energy_amount": renewable_energy},
        )


def setup_transfer_certificate(cpo: Entity, year: int):
    client = EntityFactory.create(
        name="Opérateur électricité Test",
        entity_type=Entity.OPERATOR,
        has_elec=True,
        is_tiruert_liable=True,
        registered_country=setup_france(),
    )
    set_user_access(setup_regular_user(), client, UserRights.RW)
    ElecTransferCertificate.objects.get_or_create(
        supplier=cpo,
        client=client,
        transfer_date=date(year, 8, 15),
        defaults={
            "status": ElecTransferCertificate.ACCEPTED,
            "accepted_date": date(year, 8, 16),
            "energy_amount": 2,
            "comment": "Cession de démonstration",
        },
    )


def create_sample_data():
    cpo = setup_cpo()
    existing_meter = ElecMeter.objects.filter(
        charge_point__cpo=cpo, mid_certificate="MID-DEMO-0001", initial_index_date__isnull=False
    ).first()
    year = existing_meter.initial_index_date.year + 1 if existing_meter else timezone.localdate().year - 1
    meters = setup_charge_points(cpo, year)
    setup_meter_readings(cpo, meters, year)
    setup_transfer_certificate(cpo, year)
