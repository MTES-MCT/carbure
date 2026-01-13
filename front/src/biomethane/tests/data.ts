import { AnnualDeclarationStatus } from "biomethane/types"

export const currentAnnualDeclaration = {
  year: 2025,
  status: AnnualDeclarationStatus.IN_PROGRESS,
  missing_fields: {
    digestate_missing_fields: [],
    energy_missing_fields: [],
    supply_plan_valid: true,
  },
  is_complete: true,
  producer: 1,
}

export const currentAnnualDeclarationMissingFields = {
  ...currentAnnualDeclaration,
  missing_fields: {
    digestate_missing_fields: ["digestate_field_1"],
    energy_missing_fields: ["energy_field_1"],
    supply_plan_valid: false,
  },
  is_complete: false,
}
