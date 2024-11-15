import { EntityManager } from "carbure/hooks/entity"
import api, { Api } from "common/services/api"
import { LotDetails, StockDetails } from "transaction-details/types"
import { api as apiFetch } from "common/services/api-fetch"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    console.log("OKOKOK 59")
    // return api.get<Api<LotDetails>>("/transactions/admin/lots/details", {
    //   params: { entity_id, lot_id },
    // })

    return apiFetch.GET("/v2/transactions/lots/{id}/", {
      params: {
        query: { entity_id },
        path: { id: lot_id },
      },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
    console.log("OKOKOK 60")
    // return api.get<Api<StockDetails>>("/transactions/admin/stocks/details", {
    //   params: { entity_id, stock_id },
    // })

    return apiFetch.GET("/v2/transactions/stocks/{id}/", {
      params: {
        query: { entity_id },
        path: { id: stock_id },
      },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    console.log("VERYUNSURE 61")
    return api.post("/transactions/admin/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
      checked,
    })
  },
}

const auditor = {
  getLotDetails(entity_id: number, lot_id: number) {
    console.log("VERYUNSURE 62")
    return api.get<Api<LotDetails>>("/transactions/audit/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
    console.log("VERYUNSURE 63")
    return api.get<Api<StockDetails>>("/transactions/audit/stocks/details", {
      params: { entity_id, stock_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    console.log("VERYUNSURE 64")
    return api.post("/transactions/audit/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
      checked,
    })
  },
}

export default function pickApi(entity: EntityManager) {
  return entity.isAdmin ? admin : auditor
}
