import { Debt } from "accounting/types"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"

type BalanceDebitButtonProps = {
  // Remaining debt of the balance (biofuel, category) pair, if any
  debt?: Debt
  disabled: boolean
  onDebit: () => void
  onRepayDebt: (debt: Debt) => void
}

// A debt replaces the transfer action: it has to be repaid before using the balance
export const BalanceDebitButton = ({
  debt,
  disabled,
  onDebit,
  onRepayDebt,
}: BalanceDebitButtonProps) => {
  const { t } = useTranslation()

  if (debt) {
    return (
      <Button
        priority="secondary"
        size="small"
        onClick={() => onRepayDebt(debt)}
        disabled={disabled}
      >
        {t("Acquittement de dette")}
      </Button>
    )
  }

  return (
    <Button
      iconId="fr-icon-send-plane-line"
      priority="tertiary"
      title={t("Céder")}
      size="small"
      onClick={onDebit}
      disabled={disabled}
    />
  )
}
