import api, { Api } from "common/services/api"
import { api as apiFetch } from "common/services/api-fetch"
import { lotFormToPayload, LotFormValue } from "lot-add/components/lot-form"
import { LotDetails, StockDetails } from "./types"

export function getLotDetails(entity_id: number, lot_id: number) {
  console.log("OKOKOK 3")
  // return api.get<Api<LotDetails>>("/transactions/lots/details", {
  //   params: { entity_id, lot_id },
  // })
  return apiFetch.GET("/v2/transactions/lots/{id}/", {
    params: {
      query: { entity_id },
      path: { id: lot_id },
    },
  })
}

export function updateLot(entity_id: number, form: LotFormValue) {
  console.log("VERYUNSURE 4")
  return api.post<Api<any>>("/transactions/lots/update", {
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
  console.log("VERYUNSURE 5")
  return api.post("/transactions/lots/toggle-warning", {
    entity_id,
    lot_id,
    errors,
    checked,
  })
}

export function getStockDetails(entity_id: number, stock_id: number) {
  console.log("OKOKOK 6")
  return apiFetch.GET("/v2/transactions/stocks/{id}/", {
    params: {
      query: { entity_id },
      path: { id: stock_id },
    },
  })
}
