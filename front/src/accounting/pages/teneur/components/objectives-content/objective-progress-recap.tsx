import { RecapData } from "../recap-data"
import { EnergyObjective, MainObjective } from "../../types"
import { formatObjectiveCO2, formatObjectiveGJ } from "../../utils/formatters"
import { ExtendedUnit } from "common/types"

type EnergyObjectiveProgressRecapProps = {
  objective: Pick<EnergyObjective, "progress">
  remainingType?: "limit" | "objective"
  unit?: ExtendedUnit.GJ
}

type Co2ObjectiveProgressRecapProps = {
  objective: Pick<
    MainObjective,
    "pending_teneur" | "quantity_available" | "remaining_energy"
  >
  remainingType?: "limit" | "objective"
  unit: ExtendedUnit.tCO2ev
}

type ObjectiveProgressRecapProps =
  | EnergyObjectiveProgressRecapProps
  | Co2ObjectiveProgressRecapProps

export const ObjectiveProgressRecap = (props: ObjectiveProgressRecapProps) => {
  const { remainingType } = props

  const RemainingQuantity =
    remainingType === "limit"
      ? RecapData.RemainingQuantityBeforeLimit
      : RecapData.RemainingQuantityBeforeObjective

  if (props.unit === ExtendedUnit.tCO2ev) {
    const { objective } = props

    return (
      <ul>
        <li>
          <RecapData.TeneurDeclaredMonth
            value={formatObjectiveCO2(objective.pending_teneur)}
          />
        </li>
        {remainingType !== undefined && (
          <li>
            <RemainingQuantity
              value={formatObjectiveCO2(objective.remaining_energy)}
            />
          </li>
        )}
        <li>
          <RecapData.QuantityAvailable
            value={formatObjectiveCO2(objective.quantity_available)}
          />
        </li>
      </ul>
    )
  }

  const { progress } = props.objective

  return (
    <ul>
      <li>
        <RecapData.TeneurDeclaredMonth
          value={formatObjectiveGJ(progress.pending_teneur)}
        />
      </li>
      {remainingType !== undefined && (
        <li>
          <RemainingQuantity
            value={formatObjectiveGJ(progress.remaining_energy)}
          />
        </li>
      )}
      <li>
        <RecapData.QuantityAvailable
          value={formatObjectiveGJ(progress.quantity_available)}
        />
      </li>
    </ul>
  )
}
