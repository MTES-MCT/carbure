import { useParams } from "react-router-dom"

export type EntitySelection = number | null

export default function useEntity(): EntitySelection {
  const params: { entity: string } = useParams()
  const entity = parseInt(params.entity, 10)

  return isNaN(entity) ? null : entity
}
