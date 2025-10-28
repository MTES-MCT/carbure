import { AnnualDeclarationStatus } from "biomethane/types"

export const currentAnnualDeclaration = {
  year: 2025,
  status: AnnualDeclarationStatus.IN_PROGRESS,
  missing_fields: {
    digestate_missing_fields: [],
    energy_missing_fields: [],
  },
  is_complete: true,
}
