import { Operation } from "accounting/types"
import { formatValue, getOperationQuantity } from "../../../operations.utils"
import { CONVERSIONS } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"

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
    formatUnit(quantity)
  )} / ${getOperationQuantity(
    formatUnit(CONVERSIONS.energy.MJ_TO_GJ(quantityMj), {
      unit: ExtendedUnit.GJ,
    })
  )}`
}
