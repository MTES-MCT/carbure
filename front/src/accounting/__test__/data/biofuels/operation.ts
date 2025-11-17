import { Operation, OperationSector, OperationType } from "accounting/types"
import { country } from "common/__test__/data"
import { CategoryEnum, Unit } from "common/types"

export const operationCredit: Operation = {
  id: 1,
  type: OperationType.TRANSFERT,
  sector: OperationSector.ESSENCE,
  customs_category: CategoryEnum.CONV,
  biofuel: "ETH",
  renewable_energy_share: 1,
  credited_entity: {
    id: 1,
    name: "Entity 1",
  },
  debited_entity: {
    id: 2,
    name: "Entity 2",
  },
  from_depot: {
    id: 1,
    name: "Depot 1",
  },
  to_depot: {
    id: 2,
    name: "Depot 2",
  },
  _entity: "Entity 1",
  _depot: "Depot 1",
  quantity: 1000,
  quantity_renewable: 1000,
  unit: Unit.l,
  export_country: country,
  created_at: "2021-01-01T00:00:00Z",
  quantity_mj: 27000,
  avoided_emissions: 100,
}

export const operationDebit: Operation = {
  ...operationCredit,
  quantity: -1000,
  quantity_renewable: -1000,
  quantity_mj: -27000,
}
