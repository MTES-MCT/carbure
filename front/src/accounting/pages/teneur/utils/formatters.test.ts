import { describe, expect, it } from "vitest"
import {
  computeRemainingEnergyWithAdditionalQuantityMj,
  remainingEnergyMjFrom,
  remainingGjAfterAdditionalMj,
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

describe("remainingGjAfterAdditionalMj", () => {
  const capObjective = {
    target_mj: 340_000,
    teneur_declared_mj: 0,
    pending_teneur_mj: 0,
  }
  const pci = 34

  it("ceil-displays remaining GJ when liters are just below the cap max", () => {
    const additionalMj = 9_999.98 * pci

    expect(remainingGjAfterAdditionalMj(capObjective, additionalMj)).toBe(0.001)
  })

  it("returns 0 GJ when the cap is exactly reached", () => {
    expect(remainingGjAfterAdditionalMj(capObjective, 340_000)).toBe(0)
  })
})
