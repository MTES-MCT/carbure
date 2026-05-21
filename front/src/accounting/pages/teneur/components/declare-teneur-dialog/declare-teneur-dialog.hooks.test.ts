import { renderHook } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { balance } from "accounting/__test__/data/balances"
import { defaultCategoryObjective } from "../../__test__/data"
import { CategoryObjective } from "../../types"
import { useCalculateQuantityMax } from "./declare-teneur-dialog.hooks"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"

const createObjective = (
  overrides: Partial<CategoryObjective> = {}
): CategoryObjective => ({
  ...defaultCategoryObjective,
  ...overrides,
})

const createValues = (
  overrides: Partial<DeclareTeneurDialogForm> = {}
): DeclareTeneurDialogForm => ({
  ...overrides,
})

describe("useCalculateQuantityMax", () => {
  it("returns 0 when no balance is selected", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(createObjective(), createValues())
    )

    expect(result.current).toBe(0)
  })

  it("returns the floored available balance when the objective target is falsy", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective({ target: 0 }),
        createValues({
          balance: { ...balance, available_balance: 1_234.56 },
        })
      )
    )

    expect(result.current).toBe(1_234)
  })

  it("returns the floored available balance when it is lower than the remaining objective energy", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective(),
        createValues({
          balance: { ...balance, available_balance: 200.9 },
        })
      )
    )

    // remaining objective energy = 300 - 20 - 10 = 270
    expect(result.current).toBe(200)
  })

  it("returns the remaining objective energy when it is lower than the available balance", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective(),
        createValues({
          balance: { ...balance, available_balance: 10_000 },
        })
      )
    )

    expect(result.current).toBe(270)
  })

  it("returns the same value when available balance equals remaining objective energy", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective(),
        createValues({
          balance: { ...balance, available_balance: 270 },
        })
      )
    )

    expect(result.current).toBe(270)
  })

  it("floors the remaining objective energy computed from declared and pending teneur", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective({
          target: 1_000.9,
          teneur_declared: 100.4,
          pending_teneur: 50.6,
        }),
        createValues({
          balance: { ...balance, available_balance: 10_000 },
        })
      )
    )

    expect(result.current).toBe(850)
  })

  it("returns 0 when the available balance is 0", () => {
    const { result } = renderHook(() =>
      useCalculateQuantityMax(
        createObjective(),
        createValues({
          balance: { ...balance, available_balance: 0 },
        })
      )
    )

    expect(result.current).toBe(0)
  })
})
