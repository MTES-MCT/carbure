import { describe, expect, it } from "vitest"
import { balance, balanceBiofuel } from "accounting/__test__/data/balances"
import { CategoryEnum } from "common/types"
import {
  findDebt,
  getDebtRepaymentMaxQuantity,
  getTotalDebtVolume,
} from "./debts"

const debtConv = {
  biofuel: balanceBiofuel,
  customs_category: CategoryEnum.CONV,
  remaining_volume: 200,
}

const debtAnnexe = {
  biofuel: { ...balanceBiofuel, id: 99, code: "EMHV" },
  customs_category: CategoryEnum.ANN_IX_A,
  remaining_volume: 50,
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

describe("getDebtRepaymentMaxQuantity", () => {
  it("is capped by the remaining debt when the balance is larger", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 10000)).toBe(200)
  })

  it("is capped by the available balance when the debt is larger", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 120)).toBe(120)
  })

  it("is zero when the available balance is empty", () => {
    expect(getDebtRepaymentMaxQuantity(debtConv, 0)).toBe(0)
  })
})
