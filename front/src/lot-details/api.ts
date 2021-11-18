import api, { Api } from "common-v2/services/api"
import { LotDetails } from "./types"

export function getLotDetails(entity_id: number, lot_id: number) {
  return api.get<Api<LotDetails>>("/lots/details", {
    params: { entity_id, lot_id },
  })
}
