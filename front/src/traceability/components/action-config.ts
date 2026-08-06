import { ActionFilter } from "traceability/types"

export const DEFAULT_ACTION_COLUMNS = [
  "id",
  "holder",
  "industry",
  "material",
  "quantity",
] as const

export type ActionColumn = (typeof DEFAULT_ACTION_COLUMNS)[number]

export const DEFAULT_ACTION_FILTERS = [
  ActionFilter.material,
  ActionFilter.site,
  ActionFilter.shipping_method,
] as const

/** Clés i18n par champ (colonnes et filtres). */
export const ACTION_LABEL_KEYS: Record<string, string> = {
  id: "Id",
  holder: "Détenteur",
  industry: "Filière",
  material: "Matière",
  quantity: "Quantité de matière",
  site: "Site",
  shipping_method: "Mode de transport",
}

export type ActionLabelOverrides = Partial<Record<string, string>>
