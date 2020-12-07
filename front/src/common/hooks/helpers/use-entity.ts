import { useParams } from "react-router-dom"

import { Entity } from "../../types"
import { AppHook } from "../../../carbure/hooks"

export type EntitySelection = Entity | null

export interface EntityHook {
  entity: EntitySelection
  pending: boolean
}

export default function useEntity(app: AppHook): EntityHook {
  const params: { entity: string } = useParams()
  const entityID = parseInt(params.entity, 10)

  const entity = isNaN(entityID) ? null : app.getEntity(entityID)
  const pending = params.entity === "pending"

  return { entity, pending }
}
