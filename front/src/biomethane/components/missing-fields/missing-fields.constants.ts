import type { AnnualDeclaration } from "biomethane/types"

export enum Page {
  DIGESTATE = "digestate",
  ENERGY = "energy",
}

export const MISSING_FIELDS_HASH = "missing-fields"

export const pageToMissingFieldKey: Record<
  Page,
  Exclude<keyof AnnualDeclaration["missing_fields"], "supply_plan_valid">
> = {
  [Page.DIGESTATE]: "digestate_missing_fields",
  [Page.ENERGY]: "energy_missing_fields",
}
