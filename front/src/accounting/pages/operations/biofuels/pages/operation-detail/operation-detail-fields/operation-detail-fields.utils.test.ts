import { describe, expect, it } from "vitest"
import { Operation, OperationType } from "accounting/types"

import { formatQuantityDisplay } from "./operation-detail-fields.utils"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"

describe("formatQuantityDisplay", () => {
  const createOperation = (overrides: Partial<Operation> = {}): Operation => {
    return {
      ...operationCredit,
      ...overrides,
    } as Operation
  }

  it("Should format quantity without applying renewable_energy_share", () => {
    const operation = createOperation({
      volume: 1000,
      energy: 27000,
    })

    expect(formatQuantityDisplay(operation, false)).toEqual(
      "+1 000 litres / +27 GJ"
    )
  })

  it("Should format quantity with renewable_energy_share for incorporation operation", () => {
    const operation = createOperation({
      type: OperationType.INCORPORATION,
      volume: 1000,
      energy: 27000,
      renewable_energy_share: 0.8,
    })

    expect(formatQuantityDisplay(operation, true)).toEqual(
      "+800 litres / +21,6 GJ"
    )
  })

  it("Should not apply renewable_energy_share when applyRenewableShare is false even for incorporation", () => {
    const operation = createOperation({
      type: OperationType.INCORPORATION,
      volume: 1000,
      energy: 27000,
      renewable_energy_share: 0.8,
    })

    expect(formatQuantityDisplay(operation, false)).toEqual(
      "+1 000 litres / +27 GJ"
    )
  })

  it("Should not apply renewable_energy_share for non-incorporation operation even when applyRenewableShare is true", () => {
    const operation = createOperation({
      type: OperationType.TRANSFERT,
      volume: 1000,
      energy: 27000,
      renewable_energy_share: 0.8,
    })

    expect(formatQuantityDisplay(operation, true)).toEqual(
      "+1 000 litres / +27 GJ"
    )
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
