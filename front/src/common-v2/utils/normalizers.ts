import i18next from "i18next"
import { Normalizer, Option } from "./normalize"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
} from "common/types"
import { Filter } from "transactions-v2/types"

export const normalizeBiofuel: Normalizer<Biofuel> = (biofuel) => ({
  value: biofuel,
  label: i18next.t(biofuel.code, { ns: "biofuels" }),
})

export const normalizeFeedstock: Normalizer<Feedstock> = (feedstock) => ({
  value: feedstock,
  label: i18next.t(feedstock.code, { ns: "feedstocks" }),
})

export const normalizeCountry: Normalizer<Country> = (country) => ({
  value: country,
  label: i18next.t(country.code_pays, { ns: "countries" }),
})

export const normalizeEntity: Normalizer<Entity | string> = (entity) => ({
  value: entity,
  label: isString(entity) ? entity : entity.name,
})

// prettier-ignore
export const normalizeProductionSite: Normalizer<ProductionSite | string> = (ps) => ({
  value: ps,
  label: isString(ps) ? ps : ps.name,
})

export const normalizeDepot: Normalizer<Depot | string> = (depot) => ({
  value: depot,
  label: isString(depot) ? depot : depot.name,
})

// prettier-ignore
export const normalizeFeedstockFilter: Normalizer<Option, string> = (feedstock) => ({
  value: feedstock.value,
  label: i18next.t(feedstock.value, { ns: "feedstocks" }),
})

// prettier-ignore
export const normalizeBiofuelFilter: Normalizer<Option, string> = (biofuel) => ({
  value: biofuel.value,
  label: i18next.t(biofuel.value, { ns: "biofuels" }),
})

// prettier-ignore
export const normalizeCountryFilter: Normalizer<Option, string> = (country) => ({
  value: country.value,
  label: i18next.t(country.value, { ns: "countries" }),
})

export function identity<T>(value: T) {
  return value
}

export function isString(value: any): value is string {
  return typeof value === "string"
}
