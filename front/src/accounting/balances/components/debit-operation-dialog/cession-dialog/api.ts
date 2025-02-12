import { OperationBiofuelCategory, OperationSector } from "accounting/types"
import { api } from "common/services/api-fetch"

export const getVolumeByDepot = (
  entity_id: number,
  sector: string,
  category: string,
  biofuel: string,
  depotName: string
) => {
  return api
    .GET("/tiruert/operations/balance/", {
      params: {
        query: {
          entity_id,
          sector: [sector as OperationSector],
          biofuel: [biofuel],
          customs_category: [category as OperationBiofuelCategory],
          depot: [depotName],
        },
      },
    })
    .then((res) => {
      const results = res.data?.results
      if (results) {
        return results[0]?.available_balance
      }
      return undefined
    })
}
