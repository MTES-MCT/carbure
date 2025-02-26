import { Depot, EntityPreview } from "carbure/types"
import { apiTypes } from "common/services/api-fetch.types"
export enum CessionStepKey {
  FromDepot = "from_depot",
  Quantity = "quantity",
  ToDepot = "to_depot",
  Recap = "recap",
}

export type SessionDialogForm = {
  from_depot?: apiTypes["BalanceDepot"]
  quantity?: number
  avoided_emissions_min?: number // Range determined by the simulation
  avoided_emissions_max?: number // Range determined by the simulation
  avoided_emissions?: number // Value selected by the user
  credited_entity?: EntityPreview
  to_depot?: Depot
}
