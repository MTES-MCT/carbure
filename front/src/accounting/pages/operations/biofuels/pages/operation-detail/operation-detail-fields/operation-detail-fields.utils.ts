import { Operation, OperationType } from "accounting/types"
import { Field, MappingField } from "./operation-detail.types"

export const getFields = (
  operation: Operation,
  // tous les champs conditionnels
  conditionalFields: Field[],
  // noms des champs à afficher en fonction du type d'opération
  mappingFields: MappingField[]
) => {
  // get conditional fields name based on the operation type
  const conditionalFieldsNames =
    mappingFields.find(({ type }) => type === operation.type)?.fields ?? []

  // Get conditional fields based on the conditional fields names
  const computedFields = conditionalFields.filter(({ name }) =>
    conditionalFieldsNames.includes(name)
  )

  return computedFields
}

// Format the value only for the incorporation operation
export const formatValue = (operation: Operation, value: number) => {
  if (!operation) return 0

  return operation.type === OperationType.INCORPORATION
    ? value * operation.renewable_energy_share
    : value
}
