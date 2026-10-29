import i18next from "i18next"

import { formatNumber, formatUnit } from "common/utils/formatters"

import {
  ActionStatus,
  ActionTotalEmissions,
  ActionType,
} from "traceability/types"
import { ExtendedUnit, ExtendedUnitType } from "common/types"

export const ACTION_EMISSIONS_UNIT = ExtendedUnit.gCO2eqMJ

// Format a decimal value
export function formatActionDecimal(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return ""
  return formatNumber(Number(value), { fractionDigits: 3 })
}

// Format a decimal value with a unit
export function formatUnitActionDecimal(
  value: string | number | null | undefined,
  unit: ExtendedUnitType
) {
  if (value === null || value === undefined || value === "") return ""
  return formatUnit(Number(value), unit, { fractionDigits: 3 })
}

export function formatActionTotalEmissions(
  totalEmissions: ActionTotalEmissions | null | undefined
) {
  return formatActionDecimal(totalEmissions?.total)
}

export function getActionTypeLabel(type: ActionType) {
  const labelMapping: Record<ActionType, string> = {
    [ActionType.INIT]: i18next.t("Initialisation"),
    [ActionType.PRODUCE]: i18next.t("Production"),
    [ActionType.MOVE]: i18next.t("Transport"),
    [ActionType.CONSUME]: i18next.t("Consommation"),
    [ActionType.VALORIZE]: i18next.t("Valorisation"),
  }
  return labelMapping[type]
}

export function getActionStatusLabel(status: ActionStatus) {
  const labelMapping: Record<ActionStatus, string> = {
    [ActionStatus.CREATED]: i18next.t("Créé"),
    [ActionStatus.PENDING]: i18next.t("En attente"),
    [ActionStatus.ACCEPTED]: i18next.t("Accepté"),
    [ActionStatus.REJECTED]: i18next.t("Rejeté"),
    [ActionStatus.BLOCKED]: i18next.t("Bloqué"),
    [ActionStatus.DELETED]: i18next.t("Supprimé"),
  }
  return labelMapping[status]
}
