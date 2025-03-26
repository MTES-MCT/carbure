import { findEntities } from "common/api"
import { EntityType } from "common/types"

export const findEligibleTiruertEntities = (
  entity_id: number,
  query?: string
) => {
  return findEntities(query, {
    is_enabled: true,
    is_tiruert_liable: true,
    entity_type: [
      EntityType.Producer,
      EntityType.Operator,
      EntityType.PowerOrHeatProducer,
    ],
  }).then((response) => response.filter((entity) => entity.id !== entity_id))
}
