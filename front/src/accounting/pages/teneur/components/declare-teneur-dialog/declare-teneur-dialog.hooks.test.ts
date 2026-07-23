import { renderHook } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { balance, balanceBiofuel } from "accounting/__test__/data/balances"
import { defaultCategoryObjective } from "../../__test__/data"
import { CategoryObjective } from "../../types"
import {
  computeLitersMaxFromEnergyGj,
  computeObjectiveEnergy,
  computeObjectiveProgress,
} from "../../utils/formatters"
import { useCalculateQuantityMax } from "./declare-teneur-dialog.hooks"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"

const PCI = balanceBiofuel.pci_litre

const createObjective = (
  overrides: Partial<CategoryObjective> = {}
): CategoryObjective => {
  const objective = { ...defaultCategoryObjective, ...overrides }

  return {
    ...objective,
    progress: computeObjectiveProgress(objective),
  }
}

const createValues = (
  overrides: Partial<DeclareTeneurDialogForm> = {}
): DeclareTeneurDialogForm => ({
  ...overrides,
})

const renderQuantityMax = (
  objective: CategoryObjective,
  availableBalance: number
) => {
  const { result } = renderHook(() =>
    useCalculateQuantityMax(
      objective,
      createValues({
        balance: { ...balance, available_balance: availableBalance },
      })
    )
  )

  return result.current
}

describe("useCalculateQuantityMax", () => {
  it("returns 0 when no balance is selected", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(createObjective(), createValues())
    )

    expect(result.current).toBe(0)
  })

  it("returns the floored available balance when the objective target is falsy", () => {
    expect(renderQuantityMax(createObjective({ target: 0 }), 1_234.56)).toBe(
      1_234
    )
  })

  describe("capped category — remaining GJ converted to L (ceil 2 decimals)", () => {
    const objective = createObjective()
    const remainingGj = computeObjectiveEnergy(objective)
    const maxLitersFromCap = computeLitersMaxFromEnergyGj(remainingGj, PCI)

    it("converts remaining cap to liters with ceil on 2 decimals", () => {
      // 300 − 20 − 10 = 270 GJ → ceil(270_000 / 21.1, 2) = 12 796,21 L
      expect(remainingGj).toBe(270)
      expect(maxLitersFromCap).toBe(12_796.21)
    })

    it("returns the available balance when it is lower than the cap in liters", () => {
      expect(renderQuantityMax(objective, 200.9)).toBe(200.9)
    })

    it("returns the cap in liters when the available balance is higher", () => {
      expect(renderQuantityMax(objective, 20_000)).toBe(maxLitersFromCap)
    })

    it("returns the cap in liters when it equals the available balance", () => {
      expect(renderQuantityMax(objective, maxLitersFromCap)).toBe(
        maxLitersFromCap
      )
    })
  })

  describe("capped category with fractional GJ values", () => {
    const objective = createObjective({
      target: 100.955,
      teneur_declared: 10.455,
      pending_teneur: 25.655,
    })
    const remainingGj = computeObjectiveEnergy(objective)
    const maxLitersFromCap = computeLitersMaxFromEnergyGj(remainingGj, PCI)

    it("converts fractional remaining cap to liters with ceil on 2 decimals", () => {
      // remaining = 100.955 − 10.455 − 25.655 = 64.845 GJ
      // ceil(64_845 / 21.1, 2) = 3 073,23 L
      expect(remainingGj).toBe(64.845)
      expect(maxLitersFromCap).toBe(3_073.23)
    })

    it("returns the cap in liters when the available balance is higher", () => {
      expect(renderQuantityMax(objective, 10_000.22)).toBe(maxLitersFromCap)
    })
  })

  it("returns 0 when the available balance is 0", () => {
    expect(renderQuantityMax(createObjective(), 0)).toBe(0)
  })
})
