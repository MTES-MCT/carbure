import { createContext } from "react"
import { useMatch } from "react-router-dom"
import { Entity, EntityType, ExternalAdminPages, UserRole } from "../types"
import { useUserContext } from "./user"

export const EntityContext = createContext<Entity | undefined>(undefined)

export function useEntity() {
  const user = useUserContext()
  const match = useMatch("/org/:entity/*")

  if (match === null || match.params.entity === undefined)
    throw new Error("No entity selected")

  const entityID = parseInt(match.params.entity, 10)
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

    isAdmin: type === EntityType.Administration,
    isExternalAdmin: type === EntityType.ExternalAdmin,
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

export default useEntity
