import { findFeedstocks } from "common/api"
import useEntity from "../entity"
import { useQuery } from "../async"
import { EntityType } from "common/types"

/**
 * Return a list of feedstocks with different possibilities :
 * - When the entity is an admin, return all feedstocks
 * - When the entity is a producer of biomethane, return all feedstocks that are methanogenic
 * - Otherwise, return all feedstocks that are biofuel feedstocks
 */
export const useFeedstocksByEntity = () => {
  const entity = useEntity()

  const feedstocks = useQuery(
    () =>
      findFeedstocks(
        entity.isAdmin
          ? {}
          : {
              is_biofuel_feedstock:
                entity.entity_type !== EntityType.Producteur_de_biom_thane,
              is_methanogenic: entity.isRelatedToBiomethane(),
            }
      ),
    {
      key: "feedstocks",
      params: [],
    }
  )

  return feedstocks
}
