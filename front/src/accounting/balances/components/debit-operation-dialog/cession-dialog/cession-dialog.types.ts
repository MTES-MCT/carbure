import { Depot, Entity, EntityPreview } from "carbure/types"

export enum CessionStepKey {
  FromDepot = "from_depot",
  Volume = "volume",
  ToDepot = "to_depot",
  Recap = "recap",
}

export type SessionDialogForm = {
  from_depot?: any
  volume?: number
  avoided_emissions_min?: number // Range determined by the simulation
  avoided_emissions_max?: number // Range determined by the simulation
  avoided_emissions?: number // Value selected by the user
  credited_entity?: EntityPreview
  to_depot?: Depot
}
