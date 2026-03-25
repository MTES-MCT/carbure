import { QueryOptions, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { getContract } from "./api"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { BiomethaneContract } from "./types"

export const useGetContractInfos = (
  options?: Omit<
    QueryOptions<BiomethaneContract | undefined, [number, number]>,
    "key" | "params"
  >
) => {
  const entity = useEntity()
  const { selectedEntityId } = useSelectedEntity()
  const query = useQuery(getContract, {
    key: "contract-infos",
    params: [entity.id, selectedEntityId],
    ...options,
  })

  return query
}
