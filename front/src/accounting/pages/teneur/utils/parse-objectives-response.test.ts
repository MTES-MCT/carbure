import { describe, expect, it } from "vitest"
import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import { TargetType } from "../types"
import { objectiveApiResponse } from "../__test__/objectives-api-response"
import { parseObjectivesResponse } from "./parse-objectives-response"

const emptyProgress = {
  total_teneur_declared: 0,
  base_quantity: 0,
  target_quantity: 0,
  declared_quantity: 0,
  remaining_energy: 0,
  is_objective_met: false,
  quantity_available: 0,
}

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
        progress: emptyProgress,
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
      progress: {
        total_teneur_declared: 15,
        base_quantity: 10,
        target_quantity: 100,
        declared_quantity: 5,
        remaining_energy: 85,
        is_objective_met: false,
        quantity_available: 50,
      },
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
        progress: {
          total_teneur_declared: 5,
          base_quantity: 3,
          target_quantity: 3_000,
          declared_quantity: 2,
          remaining_energy: 2_995,
          is_objective_met: false,
          quantity_available: 4,
        },
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
        target_type: TargetType.CAP,
        progress: {
          total_teneur_declared: 54.988,
          base_quantity: 4.988,
          target_quantity: 4_214.566,
          declared_quantity: 50,
          remaining_energy: 4_159.578,
          is_objective_met: false,
          quantity_available: 4_723.804,
        },
      },
      {
        code: CategoryEnum.OTHER,
        target: 0,
        teneur_declared: 10_000,
        pending_teneur: 0,
        quantity_available: 357_637.207,
        target_percent: 0,
        penalty: 0,
        target_type: TargetType.CAP,
        progress: {
          total_teneur_declared: 10_000,
          base_quantity: 10_000,
          target_quantity: 0,
          declared_quantity: 0,
          remaining_energy: 0,
          is_objective_met: false,
          quantity_available: 357_637.207,
        },
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
        target_type: TargetType.REACH,
        progress: {
          total_teneur_declared: 144,
          base_quantity: 144,
          target_quantity: 19_667.973,
          declared_quantity: 0,
          remaining_energy: 19_523.973,
          is_objective_met: false,
          quantity_available: 541_168.905,
        },
      },
    ])

    expect(parsed.unconstrained_categories).toEqual([
      {
        code: CategoryEnum.ANN_IX_B,
        target: null,
        target_percent: null,
        teneur_declared: 0,
        pending_teneur: 0,
        quantity_available: 135_531.468,
        penalty: 0,
        target_type: null,
        progress: {
          ...emptyProgress,
          quantity_available: 135_531.468,
        },
      },
    ])
  })

  it("puts categories with a null target in unconstrained categories", () => {
    const parsed = parseObjectivesResponse(objectiveApiResponse)

    expect(
      parsed.unconstrained_categories.some(
        (category) => category.code === CategoryEnum.ANN_IX_B
      )
    ).toBe(true)
    expect(
      parsed.capped_categories.some(
        (category) => category.code === CategoryEnum.ANN_IX_B
      )
    ).toBe(false)
  })
})
