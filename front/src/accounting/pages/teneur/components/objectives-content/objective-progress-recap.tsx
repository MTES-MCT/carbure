import { RecapData } from "../recap-data"
import { BaseObjective } from "../../types"
import { formatObjectiveCO2, formatObjectiveGJ } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"
import { useCallback } from "react"

type ObjectiveProgressRecapProps = {
  objective: Pick<
    BaseObjective,
    "pending_teneur" | "quantity_available" | "progress"
  >
  remainingType?: "limit" | "objective"
  unit?: ExtendedUnit
}

export const ObjectiveProgressRecap = ({
  objective,
  remainingType,
  unit = ExtendedUnit.GJ,
}: ObjectiveProgressRecapProps) => {
  const RemainingQuantity =
    remainingType === "limit"
      ? RecapData.RemainingQuantityBeforeLimit
      : RecapData.RemainingQuantityBeforeObjective

  const formatValue = useCallback(
    (value: number) => {
      if (unit === ExtendedUnit.tCO2ev) {
        return formatObjectiveCO2(value)
      }
      return formatObjectiveGJ(value)
    },
    [unit]
  )

  return (
    <ul>
      <li>
        <RecapData.TeneurDeclaredMonth
          value={formatValue(objective.pending_teneur)}
        />
      </li>
      {remainingType !== undefined && (
        <li>
          <RemainingQuantity
            value={formatValue(objective.progress.remaining_energy)}
          />
        </li>
      )}
      <li>
        <RecapData.QuantityAvailable
          value={formatValue(objective.quantity_available)}
        />
      </li>
    </ul>
  )
}
