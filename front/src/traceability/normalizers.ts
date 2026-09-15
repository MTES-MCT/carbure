import { Normalizer } from "common/utils/normalize"
import { ActionMaterial, ActionSite } from "traceability/types"

export const normalizeActionMaterial: Normalizer<ActionMaterial> = (
  material
) => ({
  label: material.name,
  value: material,
})

export const normalizeActionSite: Normalizer<ActionSite> = (site) => ({
  label: site.name,
  value: site,
})
