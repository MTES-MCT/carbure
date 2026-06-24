from dataclasses import dataclass

from django.core.exceptions import ObjectDoesNotExist

from biomethane.models import (
    BiomethaneAnnualDeclaration,
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
)
from core.models import Entity


def _safe_related(obj, attr):
    """Return a reverse one-to-one related object, or None when it does not exist."""
    try:
        return getattr(obj, attr)
    except ObjectDoesNotExist:
        return None


@dataclass
class ExportRowContext:
    """Preloaded data for a single producer row."""

    producer: Entity
    production_unit: BiomethaneProductionUnit | None
    contract: BiomethaneContract | None
    injection_site: BiomethaneInjectionSite | None
    digestate: BiomethaneDigestate | None
    energy: BiomethaneEnergy | None


@dataclass
class ExportContext:
    """Bulk-preloaded data shared across all export rows."""

    declarations: list[BiomethaneAnnualDeclaration]
    digestates: dict[int, BiomethaneDigestate]
    energies: dict[int, BiomethaneEnergy]

    def row_context(self, declaration: BiomethaneAnnualDeclaration) -> ExportRowContext:
        producer = declaration.producer
        producer_id = producer.id
        return ExportRowContext(
            producer=producer,
            production_unit=_safe_related(producer, "biomethane_production_unit"),
            contract=_safe_related(producer, "biomethane_contract"),
            injection_site=_safe_related(producer, "biomethane_injection_site"),
            digestate=self.digestates.get(producer_id),
            energy=self.energies.get(producer_id),
        )


def load_export_context(producer_ids, year: int) -> ExportContext:
    """Load declarations and related objects for the DREAL export."""
    declarations = list(
        BiomethaneAnnualDeclaration.objects.filter(
            producer_id__in=producer_ids,
            year=year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )
        .select_related(
            "producer",
            "producer__biomethane_contract",
            "producer__biomethane_production_unit__department",
            "producer__biomethane_injection_site",
        )
        .order_by("producer__name")
    )
    exported_producer_ids = [decl.producer_id for decl in declarations]

    digestates = {
        digestate.producer_id: digestate
        for digestate in BiomethaneDigestate.objects.filter(producer_id__in=exported_producer_ids, year=year)
    }
    energies = {
        energy.producer_id: energy
        for energy in BiomethaneEnergy.objects.filter(producer_id__in=exported_producer_ids, year=year)
    }

    return ExportContext(
        declarations=declarations,
        digestates=digestates,
        energies=energies,
    )
