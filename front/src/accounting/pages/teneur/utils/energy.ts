import { FRACTION_DIGITS_GJ } from "accounting/config"
import { ObjectiveProgressGj } from "../types"
import { truncateNumber } from "common/utils/formatters"

/** MJ → GJ for display only (truncate, never use for arithmetic). */
export const mjToDisplayGj = (mj: number) =>
  truncateNumber(mj / 1000, FRACTION_DIGITS_GJ)

export const remainingMj = (targetMj: number, ...parts: number[]) =>
  Math.max(0, targetMj - parts.reduce((sum, part) => sum + part, 0))

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
  remaining_energy: mjToDisplayGj(objective.remaining_energy_mj),
})
