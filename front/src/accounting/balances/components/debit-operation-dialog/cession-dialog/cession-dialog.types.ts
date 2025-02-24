import { Depot, Entity } from "carbure/types"

export enum CessionStepKey {
  FromDepot = "from_depot",
  Volume = "volume",
  ToDepot = "to_depot",
  Recap = "recap",
}

export type SessionDialogForm = {
  from_depot?: Depot
  from_depot_available_volume?: number // Value used to disable/enable the next step button
  volume?: number
  avoided_emissions?: number
  credited_entity?: Entity
  to_depot?: Depot
}
