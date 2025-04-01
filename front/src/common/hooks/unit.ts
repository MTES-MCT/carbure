import useEntity from "common/hooks/entity"
import { formatUnit, formatUnitOnly } from "common/utils/formatters"

/**
 * This hook formats a value according to the unit defined in the entity.
 * It returns the unit as a string and a function to format
 * a value based on the unit.
 */
export const useUnit = () => {
  const entity = useEntity()

  return {
    unit: entity.preferred_unit,
    unitLabel: formatUnitOnly(entity.preferred_unit),
    formatUnit: (value: number, fractionDigits = 2) =>
      formatUnit(value, entity.preferred_unit, fractionDigits),
  }
}
