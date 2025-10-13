import { Balance, OperationSector } from "accounting/types"
import { CategoryEnum } from "common/types"

const balanceBiofuel: Balance["biofuel"] = {
  id: 33,
  code: "ETH",
  renewable_energy_share: 0,
}

export const balance: Balance = {
  sector: OperationSector.ESSENCE,
  initial_balance: 0,
  available_balance: 10000,
  quantity: { credit: 10000, debit: 0 },
  pending_teneur: 0,
  declared_teneur: 0,
  pending_operations: 0,
  unit: "l",
  customs_category: CategoryEnum.CONV,
  biofuel: balanceBiofuel,
  ghg_reduction_min: 10,
  ghg_reduction_max: 80,
  saved_emissions: 0,
}
