import type { AnnualDeclaration } from "biomethane/types"

export enum Page {
  DIGESTATE = "digestate",
  ENERGY = "energy",
  CONTRACT = "contract",
  PRODUCTION = "production",
  INJECTION = "injection",
}

export const MISSING_FIELDS_HASH = "missing-fields"

export const pageToMissingFieldKey: Record<
  Page,
  Exclude<keyof AnnualDeclaration["missing_fields"], "supply_plan_valid">
> = {
  [Page.DIGESTATE]: "digestate_missing_fields",
  [Page.ENERGY]: "energy_missing_fields",
  [Page.CONTRACT]: "contract_missing_fields",
  [Page.PRODUCTION]: "production_unit_missing_fields",
  [Page.INJECTION]: "injection_missing_fields",
}
