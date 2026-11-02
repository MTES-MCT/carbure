import { Balance, Debt } from "accounting/types"

// Debts are tracked per (biofuel, customs category) pair, whatever the sector
export const findDebt = (
  debts: Debt[],
  balance: Pick<Balance, "biofuel" | "customs_category">
) =>
  debts.find(
    (debt) =>
      debt.biofuel.id === balance.biofuel?.id &&
      debt.customs_category === balance.customs_category
  )

export const getTotalDebtVolume = (debts: Debt[]) =>
  debts.reduce((total, debt) => total + debt.remaining_volume, 0)

// A repayment cannot exceed what is still owed nor the balance matching the filters
export const getDebtRepaymentMaxQuantity = (
  debt: Pick<Debt, "remaining_volume">,
  availableBalance: number
) => Math.max(0, Math.min(debt.remaining_volume, availableBalance))
