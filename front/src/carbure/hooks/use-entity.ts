import { useContext, createContext } from 'react'
import { useRouteMatch } from "react-router-dom"

import { Entity, ExternalAdminPages } from "common/types"
import { AppHook } from "./use-app"

export type EntitySelection = Entity | null

export const EntityContext = createContext<EntitySelection>(null)

export function hasPage(entity: EntitySelection, page: ExternalAdminPages) {
  return entity && entity.ext_admin_pages?.includes(page)
}

export default function useEntity(app: AppHook): EntitySelection {
  const match = useRouteMatch<{ entity: string }>("/org/:entity")

  if (!match) return null

  const entityID = parseInt(match.params.entity, 10)
  const rights = isNaN(entityID) ? null : app.getRights(entityID)
  const entity = rights?.entity ?? null

  return entity
}

export function useEntityContext() {
  return useContext(EntityContext)
}
