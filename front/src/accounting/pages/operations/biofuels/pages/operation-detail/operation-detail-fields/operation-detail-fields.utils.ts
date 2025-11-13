import { Operation, OperationType } from "accounting/types"
import { Field, MappingField } from "./operation-detail-fields.types"

export const getFields = (
  operation: Operation,
  // A list of fields
  allFields: Field[],
  // A list of fields to display based on the operation type
  mappingFields: MappingField[]
) => {
  // Get the fields names to display based on the operation type
  const fieldsToDisplayNames =
    mappingFields.find(({ type }) => type === operation.type)?.fields ?? []

  // Get fields to display based on their names
  const fieldsToDisplay = allFields.filter(({ name }) =>
    fieldsToDisplayNames.includes(name)
  )

  return fieldsToDisplay
}

// Format the value only for the incorporation operation
export const formatValue = (operation: Operation, value: number) => {
  if (!operation) return 0

  return operation.type === OperationType.INCORPORATION
    ? value * operation.renewable_energy_share
    : value
}
