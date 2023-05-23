import { EntityManager } from "carbure/hooks/entity"
import api, { Api } from "common/services/api"
import { LotDetails, StockDetails } from "transaction-details/types"

const admin = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/v5/admin/controls/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
    return api.get<Api<StockDetails>>("/v5/admin/controls/stocks/details", {
      params: { entity_id, stock_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    return api.post("/v5/admin/controls/lots/toggle-warning", {
      entity_id,
      lot_id,
      errors,
      checked,
    })
  },
}

const auditor = {
  getLotDetails(entity_id: number, lot_id: number) {
    return api.get<Api<LotDetails>>("/v5/audit/lots/details", {
      params: { entity_id, lot_id },
    })
  },

  getStockDetails(entity_id: number, stock_id: number) {
    return api.get<Api<StockDetails>>("/v5/audit/stocks/details", {
      params: { entity_id, stock_id },
    })
  },

  toggleWarning(
    entity_id: number,
    lot_id: number,
    errors: string[],
    checked: boolean
  ) {
    return api.post("/v5/audit/lots/toggle-warning", {
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
