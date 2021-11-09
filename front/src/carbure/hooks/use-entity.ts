import { useMatch } from "react-router-dom"
import { Entity, ExternalAdminPages } from "common/types"
import { AppHook } from "./use-app"

export type EntitySelection = Entity | null

export function useEntity(app: AppHook): EntitySelection {
  const match = useMatch<"entity">("/org/:entity/*")

  if (!match) return null

  const entityID = parseInt(match.params.entity ?? "", 10)
  const rights = isNaN(entityID) ? null : app.getRights(entityID)
  const entity = rights?.entity ?? null

  return entity
}

export function hasPage(entity: EntitySelection, page: ExternalAdminPages) {
  return entity && entity.ext_admin_pages?.includes(page)
}

export default useEntity
