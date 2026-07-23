import { describe, expect, it } from "vitest"
import {
  computeRemainingEnergyWithAdditionalQuantityMj,
  remainingEnergyMjFrom,
} from "./formatters"

describe("computeRemainingEnergyWithAdditionalQuantityMj", () => {
  const objective = {
    target_mj: 300_000,
    teneur_declared_mj: 20_000,
    pending_teneur_mj: 10_000,
  }

  it("returns the same value as remainingEnergyMjFrom when no quantity is added", () => {
    expect(computeRemainingEnergyWithAdditionalQuantityMj(objective, 0)).toBe(
      remainingEnergyMjFrom(objective)
    )
  })

  it("subtracts the additional quantity from the remaining energy", () => {
    expect(
      computeRemainingEnergyWithAdditionalQuantityMj(objective, 50_000)
    ).toBe(220_000)
  })

  it("never returns a negative value", () => {
    expect(
      computeRemainingEnergyWithAdditionalQuantityMj(objective, 1_000_000)
    ).toBe(0)
  })
})
