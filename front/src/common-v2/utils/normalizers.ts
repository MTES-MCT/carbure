import i18next from "i18next"
import { Normalizer, Option } from "./normalize"
import { Entity, EntityType, UserRole } from "carbure/types"
import { DeliveryType, LotStatus } from "transactions/types"
import {
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
  Certificate,
  EntityCertificate,
  EntityDepot,
} from "common/types"
import { formatPeriod } from "./formatters"

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
export const normalizeEntityDepot: Normalizer<EntityDepot> = (depot) => ({
  label: `${depot.blender!.name} - ${depot.depot!.name}`,
  value: depot
})

// prettier-ignore
export const normalizeCertificate: Normalizer<Certificate> = (certificate) => ({
  value: certificate,
  label: `${certificate.certificate_id} - ${certificate.certificate_holder}`,
})

// prettier-ignore
export const normalizeEntityCertificate: Normalizer<EntityCertificate,string> = (ec) => ({
  value: ec.certificate.certificate_id,
  label: `${ec.certificate.certificate_id} - ${ec.certificate.certificate_holder}`,
})

export const normalizeDeliveryType: Normalizer<DeliveryType> = (delivery) => ({
  value: delivery,
  label: getDeliveryLabel(delivery),
})

export const normalizePeriod: Normalizer<number> = (period) => ({
  value: period,
  label: formatPeriod(period),
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
export const normalizeDeliveryTypeFilter: Normalizer<Option<DeliveryType>, string> = (delivery) => ({
  value: delivery.value,
  label: getDeliveryLabel(delivery.value)
})

// prettier-ignore
export const normalizeLotStatusFilter: Normalizer<Option<LotStatus>, string> = (status) => ({
  value: status.value,
  label: getStatusLabel(status.value)
})

// prettier-ignore
export const normalizeEntityTypeFilter: Normalizer<Option<EntityType>, string> = (type) => ({
  value: type.value,
  label: getEntityTypeLabel(type.value)
})

// prettier-ignore
export const normalizeUnknownFilter: Normalizer<Option<any>, string> = (nullable) => ({
  value: nullable.value,
  label: nullable.value === "UNKNOWN" ? i18next.t("Inconnu") : nullable.label
})

export function getEntityTypeLabel(type: EntityType) {
  switch (type) {
    case EntityType.Administration:
      return i18next.t("Administration")
    case EntityType.Operator:
      return i18next.t("Opérateur")
    case EntityType.Producer:
      return i18next.t("Producteur")
    case EntityType.Auditor:
      return i18next.t("Auditeur")
    case EntityType.Trader:
      return i18next.t("Trader")
    case EntityType.ExternalAdmin:
      return i18next.t("Administration Externe")
    case EntityType.Unknown:
    default:
      return i18next.t("Inconnu")
  }
}

export function getUserRoleLabel(role: UserRole) {
  switch (role) {
    case UserRole.ReadOnly:
      return i18next.t("Lecture seule")
    case UserRole.ReadWrite:
      return i18next.t("Lecture/écriture")
    case UserRole.Admin:
      return i18next.t("Administration")
    case UserRole.Auditor:
      return i18next.t("Audit")
    default:
      return i18next.t("Autre")
  }
}

export function getStatusLabel(status: LotStatus | undefined) {
  switch (status) {
    case LotStatus.Draft:
      return i18next.t("Brouillon")
    case LotStatus.Pending:
      return i18next.t("En attente")
    case LotStatus.Accepted:
      return i18next.t("Accepté")
    case LotStatus.Rejected:
      return i18next.t("Refusé")
    case LotStatus.Frozen:
      return i18next.t("Déclaré")
    case LotStatus.Deleted:
      return i18next.t("Supprimé")
    default:
      return i18next.t("N/A")
  }
}

export function getDeliveryLabel(delivery: DeliveryType | undefined) {
  switch (delivery) {
    case DeliveryType.Blending:
      return i18next.t("Incorporation")
    case DeliveryType.Direct:
      return i18next.t("Livraison directe")
    case DeliveryType.Exportation:
      return i18next.t("Exportation")
    case DeliveryType.Processing:
      return i18next.t("Processing")
    case DeliveryType.RFC:
      return i18next.t("Mise à consommation")
    case DeliveryType.Stock:
      return i18next.t("Mise en stock")
    case DeliveryType.Trading:
      return i18next.t("Transfert sans stockage")
    case DeliveryType.Flushed:
      return i18next.t("Vidé")
    case DeliveryType.Unknown:
    default:
      return i18next.t("En attente")
  }
}

export function identity<T>(value: T) {
  return value
}

export function isString(value: any): value is string {
  return typeof value === "string"
}
