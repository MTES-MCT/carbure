import { createContext } from "react"
import { useMatch } from "react-router-dom"
import { Entity, EntityType, ExternalAdminPages, UserRole } from "../types"
import { useUserContext } from "./user"

export interface EntityManager extends Entity {
  isBlank: boolean
  isAdmin: boolean
  isExternal: boolean
  isAuditor: boolean
  isProducer: boolean
  isOperator: boolean
  isTrader: boolean
  hasPage: (page: ExternalAdminPages) => boolean
  hasRights: (...roles: UserRole[]) => boolean
}

export function useEntity(): EntityManager {
  const user = useUserContext()
  const match = useMatch("/org/:entity/*")

  const entityID = parseInt(match?.params.entity ?? "-1", 10)
  const entityRights = user.getRights(entityID)
  const entity = entityRights?.entity
  const type = entity?.entity_type

  return {
    id: entityID,
    name: entity?.name ?? "",
    entity_type: entity?.entity_type ?? EntityType.Operator,
    has_mac: entity?.has_mac ?? false,
    has_trading: entity?.has_trading ?? false,
    default_certificate: entity?.default_certificate ?? "",
    ext_admin_pages: entity?.ext_admin_pages ?? [],

    isBlank: entityID === -1,
    isAdmin: type === EntityType.Administration,
    isExternal: type === EntityType.ExternalAdmin,
    isAuditor: type === EntityType.Auditor,
    isProducer: type === EntityType.Producer,
    isOperator: type === EntityType.Operator,
    isTrader: type === EntityType.Trader,

    hasPage: (page: ExternalAdminPages) =>
      entity?.ext_admin_pages?.includes(page) ?? false,

    hasRights: (...roles: UserRole[]) =>
      Boolean(entityRights) && roles.includes(entityRights!.role),
  }
}

export const EntityContext = createContext<Entity | undefined>(undefined)

export default useEntity
