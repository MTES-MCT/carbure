import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { getContract } from "../pages/contract/api"

export const useGetContractInfos = () => {
  const entity = useEntity()
  const query = useQuery(getContract, {
    key: "contract-infos",
    params: [entity.id],
  })

  return query
}
