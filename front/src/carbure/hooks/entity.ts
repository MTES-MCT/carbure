import useLocalStorage from "common-v2/hooks/storage"
import { Unit } from "common/types"
import { useMatch } from "react-router-dom"
import { Entity, EntityType, ExternalAdminPages, UserRole } from "../types"
import { useUser } from "./user"

export interface EntityManager extends Entity {
  isBlank: boolean
  isAdmin: boolean
  isExternal: boolean
  isAuditor: boolean
  isProducer: boolean
  isOperator: boolean
  isTrader: boolean
  isIndustry: boolean
  canTrade: boolean
  hasPage: (page: ExternalAdminPages) => boolean
  hasRights: (...roles: UserRole[]) => boolean
  setUnit: (unit: Unit) => void
}

export function useEntity(): EntityManager {
  const user = useUser()
  const match = useMatch("/org/:entity/*")

  const entityID = parseInt(match?.params.entity ?? "-1", 10)
  const entityRights = user.getRights(entityID)
  const entity = entityRights?.entity
  const type = entity?.entity_type

  const [unit, setUnit] = useLocalStorage<Unit>("carbure:preferred-unit", "l")

  return {
    id: entityID,
    name: entity?.name ?? "",
    entity_type: entity?.entity_type ?? EntityType.Operator,
    legal_name: entity?.legal_name ?? "",
    registration_id: entity?.registration_id ?? "",
    sustainability_officer_phone_number:
      entity?.sustainability_officer_phone_number ?? "",
    sustainability_officer: entity?.sustainability_officer ?? "",
    registered_address: entity?.registered_address ?? "",
    has_mac: entity?.has_mac ?? false,
    has_trading: entity?.has_trading ?? false,
    has_stocks: entity?.has_stocks ?? false,
    has_direct_deliveries: entity?.has_direct_deliveries ?? false,
    preferred_unit: unit ?? "l",
    default_certificate: entity?.default_certificate ?? "",
    ext_admin_pages: entity?.ext_admin_pages ?? [],

    isBlank: entityID === -1,
    isAdmin: type === EntityType.Administration,
    isExternal: type === EntityType.ExternalAdmin,
    isAuditor: type === EntityType.Auditor,
    isProducer: type === EntityType.Producer,
    isOperator: type === EntityType.Operator,
    isTrader: type === EntityType.Trader,
    isIndustry: isIndustry(type),

    canTrade: !!entity?.has_stocks || !!entity?.has_trading,

    hasPage: (page: ExternalAdminPages) =>
      entity?.ext_admin_pages?.includes(page) ?? false,

    hasRights: (...roles: UserRole[]) =>
      (entityRights && roles.includes(entityRights.role)) ?? false,

    setUnit,
  }
}

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
