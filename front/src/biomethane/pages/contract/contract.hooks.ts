import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { getContract } from "./api"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useGetContractInfos = () => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const query = useQuery(getContract, {
    key: "contract-infos",
    params: [entity.id, selectedEntityId],
  })

  return query
}
