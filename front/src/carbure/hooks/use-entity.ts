import { useRouteMatch } from "react-router-dom"

import { Entity } from "common/types"
import { AppHook } from "./use-app"

export type EntitySelection = Entity | null

export default function useEntity(app: AppHook): EntitySelection {
  const match = useRouteMatch<{ entity: string }>("/org/:entity")

  if (!match) return null

  const entityID = parseInt(match.params.entity, 10)
  const rights = isNaN(entityID) ? null : app.getRights(entityID)
  const entity = rights?.entity ?? null

  return entity
}
