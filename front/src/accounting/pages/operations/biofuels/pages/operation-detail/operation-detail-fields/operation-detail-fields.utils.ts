import { Operation } from "accounting/types"
import { formatValue, getOperationQuantity } from "../../../operations.utils"
import { CONVERSIONS, formatUnit } from "common/utils/formatters"
import { ExtendedUnit, Unit } from "common/types"
import { FRACTION_DIGITS_GJ, FRACTION_DIGITS_LITERS } from "accounting/config"

export const formatQuantityDisplay = (
  operation: Operation,
  applyRenewableShare: boolean = false
) => {
  const quantity = applyRenewableShare
    ? formatValue(operation, operation.volume)
    : operation.volume

  const quantityMj = applyRenewableShare
    ? formatValue(operation, operation.energy)
    : operation.energy

  return `${getOperationQuantity(
    formatUnit(quantity, Unit.l, {
      fractionDigits: FRACTION_DIGITS_LITERS,
    })
  )} / ${getOperationQuantity(
    formatUnit(CONVERSIONS.energy.MJ_TO_GJ(quantityMj), ExtendedUnit.GJ, {
      fractionDigits: FRACTION_DIGITS_GJ,
    })
  )}`
}
