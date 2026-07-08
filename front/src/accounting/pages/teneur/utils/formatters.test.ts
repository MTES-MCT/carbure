import { describe, expect, it } from "vitest"
import {
  computeObjectiveEnergy,
  computeRemainingEnergyWithAdditionalQuantity,
} from "./formatters"

describe("computeRemainingEnergyWithAdditionalQuantity", () => {
  const objective = {
    target: 300,
    teneur_declared: 20,
    pending_teneur: 10,
    quantity_available: 0,
  }

  it("returns the same value as computeObjectiveEnergy when no quantity is added", () => {
    expect(computeRemainingEnergyWithAdditionalQuantity(objective, 0)).toBe(
      computeObjectiveEnergy({ ...objective })
    )
  })

  it("subtracts the additional quantity from the remaining energy", () => {
    expect(computeRemainingEnergyWithAdditionalQuantity(objective, 50)).toBe(
      220
    )
  })

  it("never returns a negative value", () => {
    expect(computeRemainingEnergyWithAdditionalQuantity(objective, 1_000)).toBe(
      0
    )
  })
})
