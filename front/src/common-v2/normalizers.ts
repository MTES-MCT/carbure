import i18next from "i18next"
import { Normalizer } from "./utils/normalize"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
} from "common/types"

export const normalizeBiofuel: Normalizer<Biofuel> = (biofuel) => ({
  key: biofuel.code,
  label: i18next.t(biofuel.code, { ns: "biofuels" }),
})

export const normalizeFeedstock: Normalizer<Feedstock> = (feedstock) => ({
  key: feedstock.code,
  label: i18next.t(feedstock.code, { ns: "feedstocks" }),
})

export const normalizeCountry: Normalizer<Country> = (country) => ({
  key: country.code_pays,
  label: i18next.t(country.code_pays, { ns: "countries" }),
})

export const normalizeEntity: Normalizer<Entity | string> = (entity) => ({
  key: isString(entity) ? entity : `${entity.id}`,
  label: isString(entity) ? entity : entity.name,
})

// prettier-ignore
export const normalizeProductionSite: Normalizer<ProductionSite | string> = (ps) => ({
  key: isString(ps) ? ps : `${ps.id}`,
  label: isString(ps) ? ps : ps.name,
})

export const normalizeDepot: Normalizer<Depot | string> = (depot) => ({
  key: isString(depot) ? depot : `${depot.depot_id}`,
  label: isString(depot) ? depot : depot.name,
})

export function identity<T>(value: T) {
  return value
}

export function id(
  value: Record<string, any> | string | undefined,
  key: string = "id"
) {
  return typeof value === "string" ? undefined : value?.[key]
}

export function isString(value: any): value is string {
  return typeof value === "string"
}
