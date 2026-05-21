import { describe, expect, it } from "vitest"
import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import { objectiveApiResponse } from "../__test__/objectives-api-response"
import { parseObjectivesResponse } from "./parse-objectives-response"

describe("parseObjectivesResponse", () => {
  it("returns default values when the API response is undefined", () => {
    expect(parseObjectivesResponse(undefined)).toEqual({
      global: {
        target: 0,
        teneur_declared: 0,
        pending_teneur: 0,
        quantity_available: 0,
        target_percent: 0,
        penalty: 0,
        energy_basis: 0,
      },
      sectors: [],
      capped_categories: [],
      objectivized_categories: [],
      unconstrained_categories: [],
    })
  })

  it("parses the global objective", () => {
    const { global } = parseObjectivesResponse(objectiveApiResponse)

    expect(global).toEqual({
      target: 100,
      teneur_declared: 10,
      pending_teneur: 5,
      quantity_available: 50,
      target_percent: 5,
      penalty: 100,
      energy_basis: 5,
    })
  })

  it("parses sector objectives with MJ to GJ conversion", () => {
    const { sectors } = parseObjectivesResponse(objectiveApiResponse)

    expect(sectors).toEqual([
      {
        code: OperationSector.ESSENCE,
        target: 3_000,
        teneur_declared: 3,
        pending_teneur: 2,
        quantity_available: 4,
        target_percent: 12,
        penalty: 0,
      },
    ])
  })

  it("sorts categories into capped, objectivized and unconstrained groups", () => {
    const parsed = parseObjectivesResponse(objectiveApiResponse)

    expect(parsed.capped_categories).toEqual([
      {
        code: CategoryEnum.CONV,
        target: 4_214.566,
        teneur_declared: 4.988,
        pending_teneur: 50,
        quantity_available: 4_723.804,
        target_percent: 0.67,
        penalty: 0,
      },
    ])

    expect(parsed.objectivized_categories).toEqual([
      {
        code: CategoryEnum.ANN_IX_A,
        target: 19_667.973,
        teneur_declared: 144,
        pending_teneur: 0,
        quantity_available: 541_168.905,
        target_percent: 0.67,
        penalty: 0,
      },
    ])

    expect(parsed.unconstrained_categories).toEqual([
      {
        code: CategoryEnum.OTHER,
        target: null,
        target_percent: null,
        teneur_declared: 10_000,
        pending_teneur: 0,
        quantity_available: 357_637.207,
        penalty: 0,
      },
      {
        code: CategoryEnum.ANN_IX_B,
        target: null,
        target_percent: null,
        teneur_declared: 0,
        pending_teneur: 0,
        quantity_available: 135_531.468,
        penalty: 0,
      },
    ])
  })

  it("puts categories with a zero target in unconstrained categories", () => {
    const parsed = parseObjectivesResponse(objectiveApiResponse)

    expect(
      parsed.unconstrained_categories.some(
        (category) => category.code === CategoryEnum.OTHER
      )
    ).toBe(true)
    expect(
      parsed.capped_categories.some(
        (category) => category.code === CategoryEnum.OTHER
      )
    ).toBe(false)
  })
})
