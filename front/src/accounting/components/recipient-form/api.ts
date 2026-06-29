import { findEntities } from "common/api"

export const findEligibleTiruertEntities = (
  entity_id: number,
  query?: string
) => {
  return findEntities(query, {
    is_enabled: true,
    is_tiruert_liable: true,
  }).then((response) => response.filter((entity) => entity.id !== entity_id))
}
