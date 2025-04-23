import { apiTypes } from "common/services/api-fetch.types"

export type QuantityFormProps = {
  quantity?: number
  avoided_emissions_min?: number // Range determined by the simulation
  avoided_emissions_max?: number // Range determined by the simulation
  avoided_emissions?: number // Value selected by the user
  selected_lots?: apiTypes["SimulationLotOutput"][]
}
