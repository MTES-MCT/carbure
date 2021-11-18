import api, { Api } from "common-v2/services/api"
import { StockDetails } from "./types"

export function getStockDetails(entity_id: number, stock_id: number) {
  return api.get<Api<StockDetails>>("/stocks/details", {
    params: { entity_id, stock_id },
  })
}
