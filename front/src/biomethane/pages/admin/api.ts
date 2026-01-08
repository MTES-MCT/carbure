import { findEntities } from "common/api"
import { EntityType } from "common/types"

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const getBiomethaneProducers = (entity_id: number) => {
  return findEntities("", {
    entity_type: [EntityType.Producteur_de_biom_thane],
  })
}
