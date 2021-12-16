import api, { Api } from "common-v2/services/api"
import { Lot } from "transactions-v2/types"
import { LotFormValue, lotFormToPayload } from "./components/lot-form"

export function addLot(entity_id: number, lot: LotFormValue) {
  return api.post<Api<Lot>>("/lots/add", {
    entity_id,
    ...lotFormToPayload(lot),
  })
}
