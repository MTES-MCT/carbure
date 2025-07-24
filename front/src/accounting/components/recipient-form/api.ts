import { findEntities } from "common/api"
import { EntityType } from "common/types"

export const findEligibleTiruertEntities = (
  entity_id: number,
  query?: string
) => {
  return findEntities(query, {
    is_enabled: true,
    entity_type: [EntityType.Operator],
    is_tiruert_liable: true,
    allowed_tiruert: true,
  }).then((response) => response.filter((entity) => entity.id !== entity_id))
}
