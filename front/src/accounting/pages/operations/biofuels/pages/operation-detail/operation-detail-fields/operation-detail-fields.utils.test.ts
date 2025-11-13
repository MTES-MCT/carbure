import { beforeEach, describe, expect, it, vi } from "vitest"
import { Operation, OperationType } from "accounting/types"

import { formatQuantityDisplay } from "./operation-detail-fields.utils"
import { CONVERSIONS } from "common/utils/formatters"
import { ExtendedUnit } from "common/types"
import { operationCredit } from "accounting/__test__/data/biofuels/operation"

describe("formatQuantityDisplay", () => {
  const mockFormatUnit = vi.fn(
    (value: number, options?: { unit?: ExtendedUnit }) => {
      if (options?.unit === ExtendedUnit.GJ) {
        return `${value.toFixed(2)} GJ`
      }
      return `${value.toFixed(2)} L`
    }
  )

  const createOperation = (overrides: Partial<Operation> = {}): Operation => {
    return {
      ...operationCredit,
      ...overrides,
    } as Operation
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("Integration tests", () => {
    it("Should format quantity without applying renewable_energy_share", () => {
      const operation = createOperation({
        quantity: 1000,
        quantity_mj: 27000,
      })

      const result = formatQuantityDisplay(operation, mockFormatUnit, false)

      expect(mockFormatUnit).toHaveBeenNthCalledWith(1, 1000)
      expect(mockFormatUnit).toHaveBeenNthCalledWith(
        2,
        CONVERSIONS.energy.MJ_TO_GJ(27000),
        { unit: ExtendedUnit.GJ }
      )
      expect(result).toEqual("+1000.00 L / +27.00 GJ")
    })

    it("Should format quantity with renewable_energy_share for incorporation operation", () => {
      const operation = createOperation({
        type: OperationType.INCORPORATION,
        quantity: 1000,
        quantity_mj: 27000,
        renewable_energy_share: 0.8,
      })

      const result = formatQuantityDisplay(operation, mockFormatUnit, true)

      // Should multiply by renewable_energy_share (0.8)
      const expectedQuantity = 1000 * 0.8
      const expectedQuantityMj = 27000 * 0.8

      expect(mockFormatUnit).toHaveBeenCalledWith(expectedQuantity)
      expect(mockFormatUnit).toHaveBeenCalledWith(
        CONVERSIONS.energy.MJ_TO_GJ(expectedQuantityMj),
        { unit: ExtendedUnit.GJ }
      )
      expect(result).toEqual("+800.00 L / +21.60 GJ")
    })

    it("Should not apply renewable_energy_share when applyRenewableShare is false even for incorporation", () => {
      const operation = createOperation({
        type: OperationType.INCORPORATION,
        quantity: 1000,
        quantity_mj: 27000,
        renewable_energy_share: 0.8,
      })

      const result = formatQuantityDisplay(operation, mockFormatUnit, false)

      expect(mockFormatUnit).toHaveBeenCalledWith(1000)
      expect(mockFormatUnit).toHaveBeenCalledWith(
        CONVERSIONS.energy.MJ_TO_GJ(27000),
        { unit: ExtendedUnit.GJ }
      )
      expect(result).toEqual("+1000.00 L / +27.00 GJ")
    })

    it("Should not apply renewable_energy_share for non-incorporation operation even when applyRenewableShare is true", () => {
      const operation = createOperation({
        type: OperationType.TRANSFERT,
        quantity: 1000,
        quantity_mj: 27000,
        renewable_energy_share: 0.8,
      })

      const result = formatQuantityDisplay(operation, mockFormatUnit, true)

      // formatValue should not multiply for non-incorporation operations
      expect(mockFormatUnit).toHaveBeenCalledWith(1000)
      expect(mockFormatUnit).toHaveBeenCalledWith(
        CONVERSIONS.energy.MJ_TO_GJ(27000),
        { unit: ExtendedUnit.GJ }
      )
      expect(result).toEqual("+1000.00 L / +27.00 GJ")
    })

    it("Should handle negative quantities correctly", () => {
      const operation = createOperation({
        quantity: -1000,
        quantity_mj: -27000,
      })

      const result = formatQuantityDisplay(operation, mockFormatUnit, false)

      expect(mockFormatUnit).toHaveBeenCalledWith(-1000)
      expect(mockFormatUnit).toHaveBeenCalledWith(
        CONVERSIONS.energy.MJ_TO_GJ(-27000),
        { unit: ExtendedUnit.GJ }
      )
      expect(result).toEqual("-1000.00 L / -27.00 GJ")
    })
  })
})
