import { Operation } from "accounting/types"
import { getOperationQuantity } from "../../../operations.utils"
import { CONVERSIONS, formatUnit } from "common/utils/formatters"
import { ExtendedUnit, Unit } from "common/types"
import { FRACTION_DIGITS_GJ, FRACTION_DIGITS_LITERS } from "accounting/config"

export const formatQuantityDisplay = (
  operation: Operation,
  applyRenewableShare: boolean = false
) => {
  const formatQuantity = (
    value: number,
    unit: Unit | ExtendedUnit,
    fractionDigits: number
  ) => getOperationQuantity(formatUnit(value, unit, { fractionDigits }))

  const volume = formatQuantity(
    operation.volume,
    Unit.l,
    FRACTION_DIGITS_LITERS
  )

  if (applyRenewableShare) return volume

  const energy = formatQuantity(
    CONVERSIONS.energy.MJ_TO_GJ(operation.energy),
    ExtendedUnit.GJ,
    FRACTION_DIGITS_GJ
  )

  return `${volume} / ${energy}`
}

export const formatEnergyDisplay = (operation: Operation) => {
  return `${getOperationQuantity(
    formatUnit(CONVERSIONS.energy.MJ_TO_GJ(operation.energy), ExtendedUnit.GJ, {
      fractionDigits: FRACTION_DIGITS_GJ,
    })
  )}`
}
