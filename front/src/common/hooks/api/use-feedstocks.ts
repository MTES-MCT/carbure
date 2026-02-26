import { findFeedstocks } from "common/api"
import useEntity from "../entity"
import { useQuery } from "../async"
import { useMemo } from "react"

export const useFeedstockParams = () => {
  const entity = useEntity()
  return useMemo(() => {
    if (entity.isAdmin) {
      return {}
    }
    if (entity.isRelatedToBiomethane()) {
      return {
        is_methanogenic: true,
      }
    }
    return { is_biofuel_feedstock: true }
  }, [entity])
}
/**
 * Return a list of feedstocks with different possibilities :
 * - When the entity is an admin, return all feedstocks
 * - When the entity is a producer of biomethane, return all feedstocks that are methanogenic
 * - Otherwise, return all feedstocks that are biofuel feedstocks
 */
export const useFeedstocksByEntity = () => {
  const feedstockParams = useFeedstockParams()
  const feedstocks = useQuery(() => findFeedstocks(feedstockParams), {
    key: "feedstocks",
    params: [],
  })

  return feedstocks
}
