import { Unit } from "common/types"
import { Action } from "traceability/types"

export const ACTION_CONVERTED_QUANTITY = {
  mass: Unit.kg,
  volume: Unit.l,
  energy: Unit.MJ,
} as const

export type ActionConvertedQuantity = keyof typeof ACTION_CONVERTED_QUANTITY
export type ActionQuantityKey = "quantity" | ActionConvertedQuantity

/** Resolve the displayed quantity: stored `quantity` + the material unit, or a converted annotation (kg / l / MJ). A missing material or conversion factor yields a null unit or value. */
export function getActionQuantity(
  action: Pick<Action, ActionQuantityKey | "material">,
  key: ActionQuantityKey
) {
  if (key === "quantity") {
    return { value: action.quantity, unit: action.material?.unit }
  }

  return { value: action[key], unit: ACTION_CONVERTED_QUANTITY[key] }
}
