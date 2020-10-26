import { useParams } from "react-router-dom"

import { Entity } from "../../services/types"
import { AppHook } from "../use-app"

export type EntitySelection = Entity | null

export default function useEntity(app: AppHook): EntitySelection {
  const params: { entity: string } = useParams()
  const entity = parseInt(params.entity, 10)

  return isNaN(entity) ? null : app.getEntity(entity)
}
