import { OperationType } from "accounting/types"
import { ReactNode } from "react"

export type Field = {
  name: OperationDetailField
  label: string
  value: ReactNode
  condition?: boolean
}

export enum OperationDetailField {
  SECTOR = "SECTOR",
  OPERATION_DATE = "OPERATION_DATE",
  CUSTOMS_CATEGORY = "CUSTOMS_CATEGORY",
  BIOFUEL = "BIOFUEL",
  QUANTITY = "QUANTITY",
  RENEWABLE_ENERGY_QUANTITY = "RENEWABLE_ENERGY_QUANTITY",
  AVOIDED_EMISSIONS = "AVOIDED_EMISSIONS",
  SENDER = "SENDER",
  RECEIVER = "RECEIVER",
  EXPORT_RECIPIENT = "EXPORT_RECIPIENT",
  FROM_DEPOT = "FROM_DEPOT",
  TO_DEPOT = "TO_DEPOT",
  EXPORT_COUNTRY = "EXPORT_COUNTRY",
  DURABILITY_PERIOD = "DURABILITY_PERIOD",
}

export type MappingField = {
  type: OperationType
  fields: OperationDetailField[]
}
