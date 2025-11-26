import { Operation, OperationType } from "accounting/types"
import { getOperationQuantity } from "../../../operations.utils"
import { CONVERSIONS } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"

// Format the value only for the incorporation operation
export const formatValue = (operation: Operation, value: number) => {
  if (!operation) return 0

  return operation.type === OperationType.INCORPORATION
    ? value * operation.renewable_energy_share
    : value
}

export const formatQuantityDisplay = (
  operation: Operation,
  formatUnit: any,
  applyRenewableShare: boolean = false
) => {
  const quantity = applyRenewableShare
    ? formatValue(operation, operation.quantity)
    : operation.quantity

  const quantityMj = applyRenewableShare
    ? formatValue(operation, operation.quantity_mj)
    : operation.quantity_mj

  return `${getOperationQuantity(
    operation,
    formatUnit(quantity)
  )} / ${getOperationQuantity(
    operation,
    formatUnit(CONVERSIONS.energy.MJ_TO_GJ(quantityMj), {
      unit: ExtendedUnit.GJ,
    })
  )}`
}
