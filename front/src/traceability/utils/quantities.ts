import { Unit } from "common/types"
import { Action } from "traceability/types"

export const ACTION_CONVERTED_QUANTITY = {
  mass: Unit.kg,
  volume: Unit.l,
  energy: Unit.MJ,
} as const

export type ActionConvertedQuantity = keyof typeof ACTION_CONVERTED_QUANTITY
export type ActionQuantityKey = "quantity" | ActionConvertedQuantity

/** Resolve the displayed quantity: stored `quantity` + native unit, or a converted annotation (kg / l / MJ). Missing factors yield a null value. */
export function getActionQuantity(
  action: Pick<Action, ActionQuantityKey | "unit">,
  key: ActionQuantityKey
) {
  if (key === "quantity") {
    return { value: action.quantity, unit: action.unit }
  }

  return { value: action[key], unit: ACTION_CONVERTED_QUANTITY[key] }
}
