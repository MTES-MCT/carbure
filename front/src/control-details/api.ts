import { EntityManager } from "common/hooks/entity"
import api, { Api } from "common/services/api"
import { LotDetails, StockDetails } from "transaction-details/types"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/transactions/admin/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
    return api.get<Api<StockDetails>>("/transactions/admin/stocks/details", {
      params: { entity_id, stock_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
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
    return api.get<Api<LotDetails>>("/transactions/audit/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
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
