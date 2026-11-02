import { getDebts } from "accounting/api/biofuels/debts"
import { Balance, Debt } from "accounting/types"
import { findDebt, getTotalDebtVolume } from "accounting/utils/debts"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"

const NO_DEBTS: Debt[] = []

export const useDebts = () => {
  const entity = useEntity()

  const { result, loading } = useQuery(getDebts, {
    key: "debts",
    params: [entity.id],
  })

  const debts = result?.data ?? NO_DEBTS

  return {
    debts,
    loading,
    totalVolume: getTotalDebtVolume(debts),
    getDebt: (balance: Pick<Balance, "biofuel" | "customs_category">) =>
      findDebt(debts, balance),
  }
}
