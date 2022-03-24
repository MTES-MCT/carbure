import api, { Api } from "common-v2/services/api"
import { lotFormToPayload, LotFormValue } from "lot-add/components/lot-form"
import { LotDetails, StockDetails } from "./types"

export function getLotDetails(entity_id: number, lot_id: number) {
  return api.get<Api<LotDetails>>("/lots/details", {
    params: { entity_id, lot_id },
  })
}

export function updateLot(entity_id: number, form: LotFormValue) {
  return api.post<Api<any>>("/lots/update", {
    entity_id,
    lot_id: form.lot?.id,
    ...lotFormToPayload(form),
  })
}

export function toggleWarning(
  entity_id: number,
  lot_id: number,
  errors: string[],
  checked: boolean
) {
  return api.post("/lots/toggle-warning", {
    entity_id,
    lot_id,
    errors,
    checked,
  })
}

export function getStockDetails(entity_id: number, stock_id: number) {
  return api.get<Api<StockDetails>>("/stocks/details", {
    params: { entity_id, stock_id },
  })
}