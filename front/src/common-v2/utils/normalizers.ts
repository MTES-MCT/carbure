import i18next from "i18next"
import { Normalizer, Option } from "./normalize"
import { Entity } from "carbure/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
  Certificate,
} from "common/types"
import { DeliveryType } from "transactions/types"

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

export const normalizeEntityOrUnknown: Normalizer<Entity | string> = (
  entity
) => ({
  value: entity,
  label: isString(entity) ? entity : entity.name,
})

export const normalizeEntity: Normalizer<Entity> = (entity) => ({
  value: entity,
  label: entity.name,
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

// prettier-ignore
export const normalizeAnomalyFilter: Normalizer<Option, string> = (anomaly) => ({
  value: anomaly.value,
  label: i18next.t(anomaly.value, { ns: 'errors'})
})

// prettier-ignore
export const normalizeCertificate: Normalizer<Certificate> = (certificate) => ({
  value: certificate,
  label: `${certificate.certificate_id} - ${certificate.certificate_holder}`,
})

export const normalizeDeliveryType: Normalizer<DeliveryType> = (type) => ({
  value: type,
  label: getDeliveryTypeLabel(type),
})

export function getDeliveryTypeLabel(type: DeliveryType) {
  switch (type) {
    case DeliveryType.Blending:
      return i18next.t("Incorporation")
    case DeliveryType.Direct:
      return i18next.t("Livraison directe")
    case DeliveryType.Export:
      return i18next.t("Export")
    case DeliveryType.Processing:
      return i18next.t("Processing")
    case DeliveryType.RFC:
      return i18next.t("Mise à consommation")
    case DeliveryType.Stock:
      return i18next.t("Mise en stock")
    case DeliveryType.Trading:
      return i18next.t("Trading sans stockage")
    case DeliveryType.Unknown:
    default:
      return i18next.t("Inconnu")
  }
}

export function identity<T>(value: T) {
  return value
}

export function isString(value: any): value is string {
  return typeof value === "string"
}
