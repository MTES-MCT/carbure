import { useMatch } from "react-router-dom"
import { createContext, useContext } from "react"
import { Entity, EntityType, ExternalAdminPages, UserRole } from "../types"
import { UserManager } from "./user"
import { PreferredUnitEnum } from "api-schema"

export interface EntityManager extends Entity {
  isBlank: boolean
  isAdmin: boolean
  isExternal: boolean
  isAuditor: boolean
  isProducer: boolean
  isAirline: boolean
  isOperator: boolean
  isTrader: boolean
  isPowerOrHeatProducer: boolean
  isIndustry: boolean
  isCPO: boolean
  canTrade: boolean
  hasAdminRight: (page: ExternalAdminPages | `${ExternalAdminPages}`) => boolean
  hasRights: (...roles: UserRole[]) => boolean
}

export function useEntityManager(
  user: UserManager,
  entityId?: number // This param is used only to mock current entity in storybook
): EntityManager {
  const match = useMatch("/org/:entity/*")

  const entityID = entityId ?? parseInt(match?.params.entity ?? "-1", 10)
  const entityRights = user.getRights(entityID)
  const entity = entityRights?.entity
  const type = entity?.entity_type

  return {
    id: entityID,
    name: entity?.name ?? "",
    is_enabled: entity?.is_enabled ?? false,
    entity_type: entity?.entity_type ?? EntityType.Operator,
    activity_description: entity?.activity_description ?? "",
    legal_name: entity?.legal_name ?? "",
    registration_id: entity?.registration_id ?? "",
    sustainability_officer_phone_number:
      entity?.sustainability_officer_phone_number ?? "",
    sustainability_officer_email: entity?.sustainability_officer_email ?? "",
    sustainability_officer: entity?.sustainability_officer ?? "",
    registered_address: entity?.registered_address ?? "",
    registered_city: entity?.registered_city ?? "",
    registered_zipcode: entity?.registered_zipcode ?? "",
    registered_country: entity?.registered_country ?? undefined,
    has_mac: entity?.has_mac ?? false,
    has_trading: entity?.has_trading ?? false,
    has_stocks: entity?.has_stocks ?? false,
    has_direct_deliveries: entity?.has_direct_deliveries ?? false,
    preferred_unit: entity?.preferred_unit ?? PreferredUnitEnum.l,
    default_certificate: entity?.default_certificate ?? "",
    has_saf: entity?.has_saf ?? false,
    has_elec: entity?.has_elec ?? false,
    ext_admin_pages: entity?.ext_admin_pages ?? [],
    isBlank: entityID === -1,
    isAdmin: type === EntityType.Administration,
    isExternal: type === EntityType.ExternalAdmin,
    isAuditor: type === EntityType.Auditor,
    isAirline: type === EntityType.Airline,
    isProducer: type === EntityType.Producer,
    isOperator: type === EntityType.Operator,
    isPowerOrHeatProducer: type === EntityType.PowerOrHeatProducer,
    isTrader: type === EntityType.Trader,
    isCPO: type === EntityType.CPO,
    isIndustry: isIndustry(type),
    canTrade: !!entity?.has_stocks || !!entity?.has_trading,
    website: entity?.website ?? "",
    vat_number: entity?.vat_number ?? "",

    hasAdminRight: (page: ExternalAdminPages | `${ExternalAdminPages}`) =>
      entity?.ext_admin_pages?.includes(page as ExternalAdminPages) ?? false,

    hasRights: (...roles: UserRole[]) =>
      (entityRights && roles.includes(entityRights.role)) ?? false,
  }
}

function useEntity() {
  const entity = useContext(EntityContext)
  if (entity === undefined) throw new Error("Entity context is undefined")
  return entity
}

export const EntityContext = createContext<EntityManager | undefined>(undefined)

const INDUSTRY = [EntityType.Producer, EntityType.Operator, EntityType.Trader]
export function isIndustry(type: EntityType | undefined) {
  if (type === undefined) return false
  else return INDUSTRY.includes(type)
}

export function useRights() {
  const entity = useEntity()

  function is(...roles: UserRole[]) {
    return entity.hasRights(...roles)
  }

  return { is }
}

export default useEntity
