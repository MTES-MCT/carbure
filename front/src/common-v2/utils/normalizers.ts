import i18next from "i18next"
import { Normalizer } from "./normalize"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
} from "common/types"

export const normalizeBiofuel: Normalizer<Biofuel> = (biofuel) => ({
  value: biofuel.code,
  label: i18next.t(biofuel.code, { ns: "biofuels" }),
})

export const normalizeFeedstock: Normalizer<Feedstock> = (feedstock) => ({
  value: feedstock.code,
  label: i18next.t(feedstock.code, { ns: "feedstocks" }),
})

export const normalizeCountry: Normalizer<Country> = (country) => ({
  value: country.code_pays,
  label: i18next.t(country.code_pays, { ns: "countries" }),
})

export const normalizeEntity: Normalizer<Entity, number> = (entity) => ({
  value: entity.id,
  label: entity.name,
})

// prettier-ignore
export const normalizeProductionSite: Normalizer<ProductionSite, number> = (ps) => ({
  value: ps.id,
  label: ps.name,
})

export const normalizeDepot: Normalizer<Depot> = (depot) => ({
  value: depot.depot_id,
  label: depot.name,
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
