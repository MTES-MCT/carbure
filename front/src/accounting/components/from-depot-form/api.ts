import {
  BalancesGroupBy,
  OperationBiofuelCategory,
  OperationSector,
} from "accounting/types"

import { api } from "common/services/api-fetch"
import { apiTypes } from "common/services/api-fetch.types"

export const getDepotsWithBalance = (
  entity_id: number,
  {
    sector,
    category,
    biofuel,
    query,
    ges_bound_min,
    ges_bound_max,
  }: {
    sector: OperationSector
    category: OperationBiofuelCategory
    biofuel: string
    query?: string
    ges_bound_min?: number
    ges_bound_max?: number
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
          ges_bound_min,
          ges_bound_max,
        },
      },
    })
    .then((res) => {
      const results = res.data?.results as apiTypes["BalanceByDepot"][]
      if (results && results.length > 0) {
        return results[0]!.depots.map((depot) => ({
          ...depot,
          available_balance: depot.quantity.credit - depot.quantity.debit,
        }))
      }

      return []
    })
}
