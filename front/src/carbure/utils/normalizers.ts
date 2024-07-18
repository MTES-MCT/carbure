import i18next from "i18next"
import { Normalizer } from "common/utils/normalize"
import {
  Conformity,
  CorrectionStatus,
  DeliveryType,
  LotStatus,
  ML,
} from "transactions/types"
import {
  Entity,
  EntityType,
  UserRole,
  Biofuel,
  Country,
  Depot,
  Feedstock,
  ProductionSite,
  Certificate,
  EntityCertificate,
  EntityDepot,
  EntityPreview,
} from "carbure/types"
import { formatPeriod } from "common/utils/formatters"

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

// prettier-ignore
export const normalizeEntityOrUnknown: Normalizer<Entity | string> = (entity) => {
  if (isString(entity)) return { value: entity, label: entity }
  else return normalizeEntity(entity)
}

export const normalizeEntityPreview: Normalizer<EntityPreview> = (entity) => ({
  label: entity.name,
  value: {
    id: entity.id,
    name: entity.name,
    entity_type: entity.entity_type,
  },
})
export const normalizeEntity: Normalizer<Entity> = (entity) => ({
  label: entity.name,
  value: {
    id: entity.id,
    name: entity.name,
    entity_type: entity.entity_type,
    has_mac: entity.has_mac,
    has_trading: entity.has_trading,
    has_direct_deliveries: entity.has_direct_deliveries,
    has_stocks: entity.has_stocks,
    has_elec: entity.has_elec,
    legal_name: entity.legal_name,
    registered_address: entity.registered_address,
    registered_country: entity.registered_country,
    registered_zipcode: entity.registered_zipcode,
    registered_city: entity.registered_city,
    registration_id: entity.registration_id,
    sustainability_officer: entity.sustainability_officer,
    sustainability_officer_phone_number:
      entity.sustainability_officer_phone_number,
  },
})

export const normalizeProductionSite: Normalizer<ProductionSite> = (ps) => ({
  value: ps,
  label: ps.name,
})

// prettier-ignore
export const normalizeProductionSiteOrUnknown: Normalizer<ProductionSite | string> = (ps) => ({
  value: ps,
  label: isString(ps) ? ps : ps.name,
})

export const normalizeDepot: Normalizer<Depot> = (depot) => ({
  value: depot,
  label: depot.name,
})

export const normalizeDepotOrUnknown: Normalizer<Depot | string> = (depot) => ({
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
export const normalizeEntityCertificate: Normalizer<EntityCertificate, string> = (ec) => ({
  value: ec.certificate.certificate_id,
  label: `${ec.certificate.certificate_id} - ${ec.certificate.certificate_holder}`,
})

export const normalizeDeliveryType: Normalizer<DeliveryType> = (delivery) => ({
  value: delivery,
  label: getDeliveryLabel(delivery),
})

export const normalizePeriod: Normalizer<string> = (period) => ({
  value: String(period),
  label: formatPeriod(period),
})

export const normalizeFeedstockFilter: Normalizer<string> = (feedstock) => ({
  value: feedstock,
  label: i18next.t(feedstock, { ns: "feedstocks" }),
})

export const normalizeBiofuelFilter: Normalizer<string> = (biofuel) => ({
  value: biofuel,
  label: i18next.t(biofuel, { ns: "biofuels" }),
})

export const normalizeCountryFilter: Normalizer<string> = (country) => ({
  value: country,
  label: i18next.t(country, { ns: "countries" }),
})

export const normalizeAnomalyFilter: Normalizer<string> = (anomaly) => ({
  value: anomaly,
  label: i18next.t(anomaly, { ns: "errors" }),
})

// prettier-ignore
export const normalizeDeliveryTypeFilter: Normalizer<DeliveryType> = (delivery) => ({
  value: delivery,
  label: getDeliveryLabel(delivery)
})

export const normalizeLotStatusFilter: Normalizer<LotStatus> = (status) => ({
  value: status,
  label: getStatusLabel(status),
})

export const normalizeEntityType: Normalizer<EntityType> = (type) => ({
  value: type,
  label: getEntityTypeLabel(type),
})

export const normalizeEntityTypeFilter: Normalizer<EntityType> = (type) => ({
  value: type,
  label: getEntityTypeLabel(type),
})

export const normalizeUnknownFilter: Normalizer<string> = (nullable) => ({
  value: nullable,
  label: nullable === "UNKNOWN" ? i18next.t("Inconnu") : nullable,
})

export const normalizePeriodFilter: Normalizer<string> = (period) => ({
  value: `${period}`,
  label: formatPeriod(period),
})

// prettier-ignore
export const normalizeCorrectionFilter: Normalizer<CorrectionStatus> = (correction) => ({
  value: correction,
  label: getCorrectionLabel(correction)
})

// prettier-ignore
export const normalizeConformityFilter: Normalizer<Conformity> = (conformity) => ({
  value: conformity,
  label: getConformityLabel(conformity)
})

// prettier-ignore
export const normalizeMLFilter: Normalizer<ML> = (ml) => ({
  value: ml,
  label: ml,
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
    case EntityType.Airline:
      return i18next.t("Compagnie aérienne")
    case EntityType.CPO:
      return i18next.t("Aménageur de bornes électriques")
    case EntityType.PowerOrHeatProducer:
      return i18next.t("Producteur d'électricité ou de chaleur")
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
/**
 * Takes an array of user roles and return an array with a couple role/translation.
 * The translation can be different from "getUserRoleLabel" function because they're used in different contexts
 * If no roles are passed, it will return all roles
 * @param roles
 */
export const getUserRoleOptions = (
  roles: UserRole[] = Object.values(UserRole)
) => {
  const OVERRIDES_ROLE_TRANSLATIONS: Partial<Record<UserRole, string>> = {
    [UserRole.Admin]: i18next.t(
      "Administration (contrôle complet de la société sur CarbuRe)"
    ),
    [UserRole.Auditor]: i18next.t("Audit (accès spécial pour auditeurs)"),
  }

  return roles.map((role) => ({
    label: OVERRIDES_ROLE_TRANSLATIONS[role] || getUserRoleLabel(role),
    value: role,
  }))
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
      return i18next.t("En attente")
    case DeliveryType.Consumption:
      return i18next.t("Consommation")
    default:
      return delivery || "N/A"
  }
}

export function getCorrectionLabel(correction: CorrectionStatus) {
  switch (correction) {
    case CorrectionStatus.NoProblem:
      return i18next.t("Pas de correction")
    case CorrectionStatus.InCorrection:
      return i18next.t("En correction")
    case CorrectionStatus.Fixed:
      return i18next.t("Corrigé")
  }
}

export function getConformityLabel(conformity: Conformity) {
  switch (conformity) {
    case "UNKNOWN":
      return i18next.t("Indéterminée")
    case "CONFORM":
      return i18next.t("Conforme")
    case "NONCONFORM":
      return i18next.t("Non conforme")
  }
}

export function identity<T>(value: T) {
  return value
}

export function isString(value: any): value is string {
  return typeof value === "string"
}
