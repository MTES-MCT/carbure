import { describe, expect, it } from "vitest"
import { Operation } from "accounting/types"

import {
  formatEnergyDisplay,
  formatQuantityDisplay,
} from "./operation-detail-fields.utils"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"

describe("formatQuantityDisplay", () => {
  const createOperation = (overrides: Partial<Operation> = {}): Operation => {
    return {
      ...operationCredit,
      ...overrides,
    } as Operation
  }

  it("Should return volume and energy without applying renewable_energy_share when applyRenewableShare is false", () => {
    const operation = createOperation({
      volume: 1000,
      energy: 27000,
    })

    expect(formatQuantityDisplay(operation, false)).toEqual(
      "+1 000 litres / +27 GJ"
    )
  })

  it("Should only return quantity without applying renewable_energy_share when applyRenewableShare is true", () => {
    const operation = createOperation({
      volume: 1000,
      energy: 27000,
      renewable_energy_share: 0.8,
    })

    expect(formatQuantityDisplay(operation, true)).toEqual("+1 000 litres")
  })

  it("Should handle negative quantities correctly", () => {
    const operation = createOperation({
      volume: -1000,
      energy: -27000,
    })

    expect(formatQuantityDisplay(operation, false)).toEqual(
      "-1 000 litres / -27 GJ"
    )
  })
})

describe("formatEnergyDisplay", () => {
  const createOperation = (overrides: Partial<Operation> = {}): Operation => {
    return {
      ...operationCredit,
      ...overrides,
    } as Operation
  }

  it("Should return only the energy formatted correctly", () => {
    const operation = createOperation({
      energy: 27000,
    })

    expect(formatEnergyDisplay(operation)).toEqual("+27 GJ")
  })

  it("Should handle negative energy correctly", () => {
    const operation = createOperation({
      energy: -27000,
    })

    expect(formatEnergyDisplay(operation)).toEqual("-27 GJ")
  })
})
