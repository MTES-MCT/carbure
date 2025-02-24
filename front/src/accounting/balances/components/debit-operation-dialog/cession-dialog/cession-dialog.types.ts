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
  avoided_emissions_min?: number // Range determined by the simulation
  avoided_emissions_max?: number // Range determined by the simulation
  avoided_emissions?: number // Value selected by the user
  credited_entity?: Entity
  to_depot?: Depot
}
