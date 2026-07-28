import { describe, expect, it } from "vitest"
import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import { TargetType } from "../types"
import { objectiveApiResponse } from "../__test__/objectives-api-response"
import { parseObjectivesResponse } from "./parse-objectives-response"

const emptyMainObjective = {
  target: 0,
  teneur_declared: 0,
  pending_teneur: 0,
  quantity_available: 0,
  target_percent: 0,
  penalty: 0,
  energy_basis_mj: 0,
  energy_basis_gj: 0,
  total_teneur_declared: 0,
  remaining_energy: 0,
  is_objective_met: false,
}

describe("parseObjectivesResponse", () => {
  it("returns default values when the API response is undefined", () => {
    expect(parseObjectivesResponse(undefined)).toEqual({
      global: emptyMainObjective,
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
      energy_basis_mj: 5_000,
      energy_basis_gj: 5,
      total_teneur_declared: 15,
      remaining_energy: 85,
      is_objective_met: false,
    })
  })

  it("parses sector objectives in MJ with GJ progress for display", () => {
    const { sectors } = parseObjectivesResponse(objectiveApiResponse)

    expect(sectors).toEqual([
      {
        code: OperationSector.ESSENCE,
        target_mj: 3_000_000,
        teneur_declared_mj: 3_000,
        pending_teneur_mj: 2_000,
        quantity_available_mj: 4_000,
        target_percent: 12,
        penalty: 0,
        total_teneur_declared_mj: 5_000,
        remaining_energy_mj: 2_995_000,
        is_objective_met: false,
        progress: {
          target: 3_000,
          teneur_declared: 3,
          pending_teneur: 2,
          quantity_available: 4,
          total_teneur_declared: 5,
          remaining_energy: 2_995,
        },
      },
    ])
  })

  it("sorts categories into capped, objectivized and unconstrained groups", () => {
    const parsed = parseObjectivesResponse(objectiveApiResponse)

    expect(parsed.capped_categories).toEqual([
      {
        code: CategoryEnum.CONV,
        target_mj: 4_214_566,
        teneur_declared_mj: 4_988,
        pending_teneur_mj: 50_000,
        quantity_available_mj: 4_723_804,
        target_percent: 0.67,
        penalty: 0,
        target_type: TargetType.CAP,
        total_teneur_declared_mj: 54_988,
        remaining_energy_mj: 4_159_578,
        is_objective_met: false,
        progress: {
          target: 4_214.566,
          teneur_declared: 4.988,
          pending_teneur: 50,
          quantity_available: 4_723.804,
          total_teneur_declared: 54.988,
          remaining_energy: 4_159.578,
        },
      },
      {
        code: CategoryEnum.OTHER,
        target_mj: 0,
        teneur_declared_mj: 10_000_000,
        pending_teneur_mj: 0,
        quantity_available_mj: 357_637_207,
        target_percent: 0,
        penalty: 0,
        target_type: TargetType.CAP,
        total_teneur_declared_mj: 10_000_000,
        remaining_energy_mj: 0,
        is_objective_met: false,
        progress: {
          target: 0,
          teneur_declared: 10_000,
          pending_teneur: 0,
          quantity_available: 357_637.207,
          total_teneur_declared: 10_000,
          remaining_energy: 0,
        },
      },
    ])

    expect(parsed.objectivized_categories).toEqual([
      {
        code: CategoryEnum.ANN_IX_A,
        target_mj: 19_667_973,
        teneur_declared_mj: 144_000,
        pending_teneur_mj: 0,
        quantity_available_mj: 541_168_905,
        target_percent: 0.67,
        penalty: 0,
        target_type: TargetType.REACH,
        total_teneur_declared_mj: 144_000,
        remaining_energy_mj: 19_523_973,
        is_objective_met: false,
        progress: {
          target: 19_667.973,
          teneur_declared: 144,
          pending_teneur: 0,
          quantity_available: 541_168.905,
          total_teneur_declared: 144,
          remaining_energy: 19_523.973,
        },
      },
    ])

    expect(parsed.unconstrained_categories).toEqual([
      {
        code: CategoryEnum.ANN_IX_B,
        target_mj: null,
        target_percent: null,
        teneur_declared_mj: 0,
        pending_teneur_mj: 0,
        quantity_available_mj: 135_531_468,
        penalty: 0,
        target_type: null,
        total_teneur_declared_mj: 0,
        remaining_energy_mj: 0,
        is_objective_met: false,
        progress: {
          target: 0,
          teneur_declared: 0,
          pending_teneur: 0,
          quantity_available: 135_531.468,
          total_teneur_declared: 0,
          remaining_energy: 0,
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
