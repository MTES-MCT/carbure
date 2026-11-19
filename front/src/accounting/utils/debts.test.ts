import { describe, expect, it } from "vitest"
import { balance, balanceBiofuel } from "accounting/__test__/data/balances"
import { CategoryEnum } from "common/types"
import { DebtType } from "accounting/types"
import {
  findDebt,
  getDebtRepaymentMaxQuantity,
  getTotalDebtVolume,
  getDebtRepaymentType,
  getDebtRepaymentTypes,
} from "./debts"

const debtConv = {
  biofuel: balanceBiofuel,
  customs_category: CategoryEnum.CONV,
  remaining_volume: 200,
  remaining_tco2: 0,
}

const debtAnnexe = {
  biofuel: { ...balanceBiofuel, id: 99, code: "EMHV" },
  customs_category: CategoryEnum.ANN_IX_A,
  remaining_volume: 50,
  remaining_tco2: 0,
}

describe("findDebt", () => {
  it("returns the debt of the balance biofuel and customs category", () => {
    expect(findDebt([debtAnnexe, debtConv], balance)).toBe(debtConv)
  })

  it("ignores a debt on the same biofuel but another customs category", () => {
    const debts = [{ ...debtConv, customs_category: CategoryEnum.ANN_IX_A }]

    expect(findDebt(debts, balance)).toBeUndefined()
  })

  it("ignores a debt on the same category but another biofuel", () => {
    const debts = [{ ...debtConv, biofuel: debtAnnexe.biofuel }]

    expect(findDebt(debts, balance)).toBeUndefined()
  })

  it("returns nothing when there is no debt", () => {
    expect(findDebt([], balance)).toBeUndefined()
  })
})

describe("getTotalDebtVolume", () => {
  it("sums the remaining volume of every debt", () => {
    expect(getTotalDebtVolume([debtConv, debtAnnexe])).toBe(250)
  })

  it("is zero without debt", () => {
    expect(getTotalDebtVolume([])).toBe(0)
  })
})

describe("getDebtRepaymentType", () => {
  const tco2Debt = {
    ...debtConv,
    remaining_volume: 0,
    remaining_tco2: 20,
  }
  const mixedDebt = { ...debtConv, remaining_tco2: 20 }

  it("switches to tCO2 when a previous volume debt is no longer open", () => {
    expect(getDebtRepaymentType(tco2Debt, DebtType.VOLUME)).toBe(DebtType.TCO2)
  })

  it("switches to volume when a previous tCO2 debt is no longer open", () => {
    expect(getDebtRepaymentType(debtConv, DebtType.TCO2)).toBe(DebtType.VOLUME)
  })

  it("requires a choice when both debts are open", () => {
    expect(getDebtRepaymentType(mixedDebt)).toBeUndefined()
    expect(getDebtRepaymentType(mixedDebt, DebtType.TCO2)).toBe(DebtType.TCO2)
    expect(getDebtRepaymentType(mixedDebt, DebtType.VOLUME)).toBe(
      DebtType.VOLUME
    )
  })
})

describe("getDebtRepaymentMaxQuantity", () => {
  it("is capped by the remaining debt when the balance is larger", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 10000)).toBe(200)
  })

  describe("getDebtRepaymentTypes", () => {
    it("opens the volume path directly when only volume is owed", () => {
      expect(getDebtRepaymentTypes(debtConv)).toEqual([DebtType.VOLUME])
    })

    it("opens the emissions path directly when only tCO2 is owed", () => {
      expect(
        getDebtRepaymentTypes({
          ...debtConv,
          remaining_volume: 0,
          remaining_tco2: 20,
        })
      ).toEqual([DebtType.TCO2])
    })

    it("offers separate repayments when both kinds of debt are open", () => {
      expect(
        getDebtRepaymentTypes({ ...debtConv, remaining_tco2: 20 })
      ).toEqual([DebtType.VOLUME, DebtType.TCO2])
    })
  })

  it("is capped by the available balance when the debt is larger", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 120)).toBe(120)
  })

  it("is zero when the available balance is empty", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 0)).toBe(0)
  })
})
