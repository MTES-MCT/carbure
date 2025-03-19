import useEntity from "common/hooks/entity"
import { ExtendedUnit, Unit } from "common/types"
import { formatUnit, formatUnitOnly } from "common/utils/formatters"

/**
 * This hook formats a value according to the unit defined in the entity.
 * It returns the unit as a string and a function to format
 * a value based on the unit.
 * If a custom unit is provided, it will be used instead of the entity's preferred unit.
 */
export const useUnit = (customUnit?: Unit | ExtendedUnit) => {
  const entity = useEntity()
  const unit = customUnit ?? entity.preferred_unit

  return {
    entityUnit: entity.preferred_unit,
    unit,
    unitLabel: formatUnitOnly(entity.preferred_unit),
    // Use the customUnit passed as parameter if provided, otherwise use the unit defined in the hook or the entity's preferred unit
    formatUnit: (
      value: number,
      {
        fractionDigits = 2,
        unit: unitParam,
      }: { fractionDigits?: number; unit?: Unit | ExtendedUnit } = {}
    ) => formatUnit(value, unitParam ?? unit, fractionDigits),
  }
}
