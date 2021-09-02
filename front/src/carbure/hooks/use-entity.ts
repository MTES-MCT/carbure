import { useRouteMatch } from "react-router-dom"

import { Entity } from "common/types"
import { AppHook } from "./use-app"

export type EntitySelection = Entity | null

export interface EntityHook {
  entity: EntitySelection
  pending: boolean
}

export default function useEntity(app: AppHook): EntityHook {
  const match = useRouteMatch<{ entity: string }>("/org/:entity")

  if (!match) return { entity: null, pending: false }

  const entityID = parseInt(match.params.entity, 10)
  const rights = isNaN(entityID) ? null : app.getRights(entityID)
  const entity = rights?.entity ?? null
  const pending = match.params.entity === "pending"

  return { entity, pending }
}
