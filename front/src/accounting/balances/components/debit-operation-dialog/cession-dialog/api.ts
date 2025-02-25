import { BalancesGroupBy } from "accounting/balances/types"
import { OperationBiofuelCategory, OperationSector } from "accounting/types"
import { api } from "common/services/api-fetch"

export const getDepotsWithBalance = (
  entity_id: number,
  {
    sector,
    category,
    biofuel,
    query,
  }: {
    sector: OperationSector
    category: OperationBiofuelCategory
    biofuel: string
    query?: string
  }
) => {
  return api
    .GET("/tiruert/operations/balance/", {
      params: {
        query: {
          entity_id,
          sector: [sector],
          biofuel: [biofuel],
          customs_category: [category],
          group_by: BalancesGroupBy.depot,
          search: query,
        },
      },
    })
    .then((res) => {
      const results = res.data?.results
      if (results && results.length > 0) {
        // @ts-ignore backend will implement
        return results[0].depots
      }
      return []
    })
}
