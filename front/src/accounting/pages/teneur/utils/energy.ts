import { FRACTION_DIGITS_GJ } from "accounting/config"
import { EnergyObjectiveFields, ObjectiveProgressGj } from "../types"
import { ceilNumber, truncateNumber } from "common/utils/formatters"

/** MJ → GJ for display only (truncate, never use for arithmetic). */
export const mjToDisplayGj = (mj: number) =>
  truncateNumber(mj / 1000, FRACTION_DIGITS_GJ)

/**
 * Remaining MJ → GJ for display.
 * GJ is truncated to 3 decimals (1 MJ resolution), so a positive remainder below 1 MJ
 * would otherwise display as 0 GJ — e.g. when declaring in liters near a cap
 * (9999.98 L × 34 MJ/L leaves 0.68 MJ). Ceil to 0.001 GJ in that case only.
 */
export const mjToRemainingDisplayGj = (mj: number) => {
  if (mj === 0) return 0

  const truncated = truncateNumber(mj / 1000, FRACTION_DIGITS_GJ)
  if (truncated === 0) {
    return ceilNumber(mj / 1000, FRACTION_DIGITS_GJ)
  }

  return truncated
}

export const remainingMj = (targetMj: number, ...parts: number[]) =>
  Math.max(0, targetMj - parts.reduce((sum, part) => sum + part, 0))

type EnergyObjectiveDeclaration = Pick<
  EnergyObjectiveFields,
  "target_mj" | "teneur_declared_mj" | "pending_teneur_mj"
>

/** Remaining cap/objective energy (MJ) after an additional declaration in the modal. */
export const remainingMjAfterDeclaration = (
  objective: EnergyObjectiveDeclaration,
  additionalMj: number
) =>
  Math.max(
    0,
    remainingMj(
      objective.target_mj ?? 0,
      objective.teneur_declared_mj,
      objective.pending_teneur_mj
    ) - additionalMj
  )

/** Same as remainingMjAfterDeclaration, converted to GJ for display. */
export const remainingGjAfterDeclaration = (
  objective: EnergyObjectiveDeclaration,
  additionalMj: number
) =>
  mjToRemainingDisplayGj(remainingMjAfterDeclaration(objective, additionalMj))

export const buildObjectiveProgressGj = (objective: {
  target_mj: number | null
  teneur_declared_mj: number
  pending_teneur_mj: number
  quantity_available_mj: number
  total_teneur_declared_mj: number
  remaining_energy_mj: number
}): ObjectiveProgressGj => ({
  target: mjToDisplayGj(objective.target_mj ?? 0),
  teneur_declared: mjToDisplayGj(objective.teneur_declared_mj),
  pending_teneur: mjToDisplayGj(objective.pending_teneur_mj),
  quantity_available: mjToDisplayGj(objective.quantity_available_mj),
  total_teneur_declared: mjToDisplayGj(objective.total_teneur_declared_mj),
  remaining_energy: mjToRemainingDisplayGj(objective.remaining_energy_mj),
})
