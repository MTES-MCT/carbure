import { Balance, Debt, DebtType } from "accounting/types"

export const getDebtRepaymentTypes = (debt: Debt): DebtType[] => [
  ...(debt.remaining_volume > 0 ? [DebtType.VOLUME] : []),
  ...(debt.remaining_tco2 > 0 ? [DebtType.TCO2] : []),
]

export const getDebtRepaymentType = (
  debt: Debt,
  selectedType?: DebtType
): DebtType | undefined => {
  const types = getDebtRepaymentTypes(debt)
  return types.length === 1
    ? types[0]
    : types.find((type) => type === selectedType)
}

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
