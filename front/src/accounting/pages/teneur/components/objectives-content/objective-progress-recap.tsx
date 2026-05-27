import { RecapData } from "../recap-data"
import { BaseObjective } from "../../types"
import { formatObjectiveGJ } from "../../utils/formatters"

type ObjectiveProgressRecapProps = {
  objective: Pick<
    BaseObjective,
    "pending_teneur" | "quantity_available" | "progress"
  >
  remainingType?: "limit" | "objective"
}

export const ObjectiveProgressRecap = ({
  objective,
  remainingType,
}: ObjectiveProgressRecapProps) => {
  const RemainingQuantity =
    remainingType === "limit"
      ? RecapData.RemainingQuantityBeforeLimit
      : RecapData.RemainingQuantityBeforeObjective

  return (
    <ul>
      <li>
        <RecapData.TeneurDeclaredMonth
          value={formatObjectiveGJ(objective.pending_teneur)}
        />
      </li>
      {remainingType !== undefined && (
        <li>
          <RemainingQuantity
            value={formatObjectiveGJ(objective.progress.remaining_energy)}
          />
        </li>
      )}
      <li>
        <RecapData.QuantityAvailable
          value={formatObjectiveGJ(objective.quantity_available)}
        />
      </li>
    </ul>
  )
}
