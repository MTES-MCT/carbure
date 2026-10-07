import { describe, expect, it } from "vitest"
import { energyFromLiters, maxLitersFromRemainingMj } from "./liters"

describe("energyFromLiters", () => {
  it("returns MJ and truncated GJ from liters and PCI", () => {
    expect(energyFromLiters(10_000, 34)).toEqual({ mj: 340_000, gj: 340 })
  })

  it("applies the renewable energy share", () => {
    expect(energyFromLiters(10_000, 34, 0.5)).toEqual({ mj: 170_000, gj: 170 })
  })
})

describe("maxLitersFromRemainingMj", () => {
  it("converts remaining MJ to max liters with ceil on 2 decimals", () => {
    expect(maxLitersFromRemainingMj(270_000, 21.1)).toBe(12_796.21)
  })

  it("uses the renewable energy share to compute the physical liters", () => {
    expect(maxLitersFromRemainingMj(270_000, 21.1, 0.5)).toBe(25_592.42)
  })
})
