import { Operation, OperationType } from "accounting/types"
import { ReactNode } from "react"

export type Field = {
  name: OperationDetailFields
  label: ReactNode
  value: ReactNode
  condition?: boolean
}

export enum OperationDetailFields {
  SECTOR = "SECTOR",
  TEST = "TEST",
}

type MappingFields = {
  type: OperationType
  fields: OperationDetailFields[]
}

// on crée un mapping en fonction de si on a envoyé ou reçu une opération et du type d'opération
const MAPPING_FIELDS_RECEIVER: MappingFields[] = [
  { type: OperationType.TRANSFERT, fields: [OperationDetailFields.TEST] },
]

const MAPPING_FIELDS_SENDER: MappingFields[] = [
  { type: OperationType.TRANSFERT, fields: [OperationDetailFields.SECTOR] },
]

export const getFields = (operation: Operation, conditionalFields: Field[]) => {
  // je recois une opération si la quantité est positive
  const isReceiver = (operation.quantity ?? 0) > 0

  const mapping = isReceiver ? MAPPING_FIELDS_RECEIVER : MAPPING_FIELDS_SENDER

  // get conditional fields name based on the operation type
  const conditionalFieldsNames =
    mapping.find(({ type }) => type === operation.type)?.fields ?? []

  // Get conditional fields based on the conditional fields names
  const computedFields = conditionalFields.filter(({ name }) =>
    conditionalFieldsNames.includes(name)
  )

  return computedFields
}
