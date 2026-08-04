import { describe, expect, it } from "vitest"
import { energyFromLiters, maxLitersFromRemainingMj } from "./liters"

describe("energyFromLiters", () => {
  it("returns MJ and truncated GJ from liters and PCI", () => {
    expect(energyFromLiters(10_000, 34)).toEqual({ mj: 340_000, gj: 340 })
  })
})

describe("maxLitersFromRemainingMj", () => {
  it("converts remaining MJ to max liters with ceil on 2 decimals", () => {
    expect(maxLitersFromRemainingMj(270_000, 21.1)).toBe(12_796.21)
  })
})
