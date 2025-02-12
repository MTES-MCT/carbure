import { Depot, Entity } from "carbure/types"

export enum CessionStepKey {
  FromDepot = "from_depot",
  Volume = "volume",
  ToDepot = "to_depot",
  Recap = "recap",
}

export type SessionDialogForm = {
  from_depot?: Depot
  volume?: number
  avoided_emissions?: number
  credited_entity?: Entity
  to_depot?: Depot
}
