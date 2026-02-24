import { findFeedstocks } from "common/api"
import useEntity from "../entity"
import { useQuery } from "../async"
import { EntityType, ExternalAdminPages } from "common/types"

export const useFeedstocksByEntity = () => {
  const entity = useEntity()

  const displayMethanogenic =
    entity.entity_type === EntityType.Producteur_de_biom_thane ||
    entity.entity_type === EntityType.Fournisseur_de_biom_thane ||
    (entity.isExternal && entity.hasAdminRight(ExternalAdminPages.DREAL))

  const feedstocks = useQuery(
    () =>
      findFeedstocks(
        entity.isAdmin
          ? {}
          : {
              is_biofuel_feedstock:
                entity.entity_type !== EntityType.Producteur_de_biom_thane,
              is_methanogenic: displayMethanogenic,
            }
      ),
    {
      key: "feedstocks",
      params: [],
    }
  )

  return feedstocks
}
