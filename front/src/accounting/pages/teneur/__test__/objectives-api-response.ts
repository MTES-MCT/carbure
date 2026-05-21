import { CategoryEnum } from "common/types"
import { OperationSector } from "accounting/types"
import { apiTypes } from "common/services/api-fetch.types"
import { TargetType } from "../types"

export const objectiveApiResponse: apiTypes["ObjectiveOutput"] = {
  main: {
    available_balance: 50,
    target: 100,
    pending_teneur: 5,
    declared_teneur: 10,
    unit: "GJ",
    penalty: 100,
    target_percent: 0.05,
    energy_basis: 5_000,
  },
  sectors: [
    {
      code: OperationSector.ESSENCE,
      pending_teneur: 2_000,
      declared_teneur: 3_000,
      available_balance: 4_000,
      unit: "MJ",
      energy_basis: 0,
      objective: {
        target_mj: 3_000_000,
        target_type: TargetType.REACH,
        penalty: 0,
        target_percent: 0.12,
      },
    },
  ],
  categories: [
    {
      code: CategoryEnum.CONV,
      pending_teneur: 50_000,
      declared_teneur: 4_988,
      available_balance: 4_723_804,
      unit: "MJ",
      objective: {
        target_mj: 4_214_566,
        target_type: TargetType.CAP,
        penalty: 0,
        target_percent: 0.0067,
      },
    },
    {
      code: CategoryEnum.ANN_IX_A,
      pending_teneur: 0,
      declared_teneur: 144_000,
      available_balance: 541_168_905,
      unit: "MJ",
      objective: {
        target_mj: 19_667_973,
        target_type: TargetType.REACH,
        penalty: 0,
        target_percent: 0.0067,
      },
    },
    {
      code: CategoryEnum.OTHER,
      pending_teneur: 0,
      declared_teneur: 10_000_000,
      available_balance: 357_637_207,
      unit: "MJ",
      objective: {
        target_mj: 0,
        target_type: TargetType.CAP,
        penalty: 0,
        target_percent: 0,
      },
    },
    {
      code: CategoryEnum.ANN_IX_B,
      pending_teneur: 0,
      declared_teneur: 0,
      available_balance: 135_531_468,
      unit: "MJ",
      objective: {
        target_mj: null as unknown as number,
        target_type: TargetType.CAP,
        penalty: 0,
        target_percent: 0,
      },
    },
  ],
}
