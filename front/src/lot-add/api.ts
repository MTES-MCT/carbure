import api, { Api } from "common/services/api"
import { Lot } from "transactions/types"
import { LotFormValue, lotFormToPayload } from "./components/lot-form"

export function addLot(entity_id: number, lot: LotFormValue) {
	return api.post<Api<Lot>>("/transactions/lots/add", {
		entity_id,
		...lotFormToPayload(lot),
	})
}
