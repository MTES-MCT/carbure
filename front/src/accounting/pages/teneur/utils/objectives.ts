/**
 * Objective enrichment and display formatting.
 * Arithmetic lives in energy.ts (MJ); progress.* fields are GJ for display only.
 */
import {
  EnergyObjective,
  EnergyObjectiveComputed,
  EnergyObjectiveFields,
  MainObjective,
  ObjectiveProgressGj,
} from "../types"
import { ExtendedUnit } from "common/types"
import { formatUnit } from "common/utils/formatters"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { mjToDisplayGj, mjToRemainingDisplayGj, remainingMj } from "./energy"

type EnergyObjectiveInput = Pick<
  EnergyObjectiveFields,
  "teneur_declared_mj" | "pending_teneur_mj" | "quantity_available_mj"
> & {
  target_mj: number | null
}

type MainObjectiveInput = Pick<
  MainObjective,
  | "teneur_declared"
  | "pending_teneur"
  | "quantity_available"
  | "target"
  | "energy_basis_mj"
  | "target_percent"
  | "penalty"
>

// ── Progress GJ (used in objective display) ──
export const buildObjectiveProgressGj = (
  objective: Pick<
    EnergyObjective,
    | "target_mj"
    | "teneur_declared_mj"
    | "pending_teneur_mj"
    | "quantity_available_mj"
    | "total_teneur_declared_mj"
    | "remaining_energy_mj"
  >
): ObjectiveProgressGj => ({
  target: mjToDisplayGj(objective.target_mj ?? 0),
  teneur_declared: mjToDisplayGj(objective.teneur_declared_mj),
  pending_teneur: mjToDisplayGj(objective.pending_teneur_mj),
  quantity_available: mjToDisplayGj(objective.quantity_available_mj),
  total_teneur_declared: mjToDisplayGj(objective.total_teneur_declared_mj),
  remaining_energy: mjToRemainingDisplayGj(objective.remaining_energy_mj),
})

// ── Enrichment (called when parsing API objectives) ──

export const enrichEnergyObjective = <T extends EnergyObjectiveInput>(
  objective: T
): T & EnergyObjectiveComputed => {
  const total_teneur_declared_mj =
    objective.teneur_declared_mj + objective.pending_teneur_mj
  const remaining_energy_mj = remainingMj(
    objective.target_mj ?? 0,
    objective.teneur_declared_mj,
    objective.pending_teneur_mj
  )
  const is_objective_met = Boolean(
    objective.target_mj &&
    objective.target_mj > 0 &&
    total_teneur_declared_mj >= objective.target_mj
  )

  const computed = {
    total_teneur_declared_mj,
    remaining_energy_mj,
    is_objective_met,
  }

  return {
    ...objective,
    ...computed,
    progress: buildObjectiveProgressGj({ ...objective, ...computed }),
  }
}

export const enrichMainObjective = <T extends MainObjectiveInput>(
  objective: T
): T &
  Pick<
    MainObjective,
    | "total_teneur_declared"
    | "remaining_energy"
    | "is_objective_met"
    | "energy_basis_gj"
  > => {
  const total_teneur_declared =
    objective.teneur_declared + objective.pending_teneur
  const remaining_energy = remainingMj(
    objective.target,
    objective.teneur_declared,
    objective.pending_teneur
  )
  const is_objective_met =
    objective.target > 0 ? total_teneur_declared >= objective.target : false

  return {
    ...objective,
    total_teneur_declared,
    remaining_energy,
    is_objective_met,
    energy_basis_gj: mjToDisplayGj(objective.energy_basis_mj),
  }
}

// ── Display (strings with unit — use formatEnergyNumber for number-only) ──

/** Pre-computed GJ value (progress.*) formatted with unit, e.g. "54,988 GJ". */
export const formatObjectiveGJ = (gj: number) =>
  formatAccountingUnit(gj, ExtendedUnit.GJ)

/** Raw MJ value formatted as GJ with unit (unenriched API balances). */
export const formatObjectiveGJFromMj = (mj: number) =>
  formatObjectiveGJ(mjToDisplayGj(mj))

export const formatObjectiveCO2 = (value: number) =>
  formatUnit(value, ExtendedUnit.tCO2ev, { fractionDigits: 0 })
