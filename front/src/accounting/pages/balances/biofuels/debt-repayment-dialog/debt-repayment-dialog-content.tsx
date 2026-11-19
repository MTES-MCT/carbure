import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { OperationText } from "accounting/components/operation-text"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
} from "accounting/components/quantity-form"
import { CreateOperationType, DebtType } from "accounting/types"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { getDebtRepaymentMaxQuantity } from "accounting/utils/debts"
import { Alert } from "common/components/alert2"
import { Box } from "common/components/scaffold"
import { useStepper } from "common/components/stepper"
import { Unit } from "common/types"
import { useTranslation } from "react-i18next"
import { DebitOperationStepperDialog } from "../debit-operation-dialog/components/debit-operation-stepper-dialog"
import {
  DebtRemainingNotice,
  DebtRepaymentTco2Summary,
  formatDebtTco2,
} from "./debt-repayment-dialog-notices"
import { DebtRepaymentDialogContentProps } from "./debt-repayment-dialog.types"
import { useDebtRepaymentDialog } from "./debt-repayment-dialog.hooks"

export const DEBT_REPAYMENT_FILTERS_STEP_KEY = "debt-repayment-filters"
export const DEBT_REPAYMENT_TCO2_STEP_KEY = "debt-repayment-tco2"

export const DebtRepaymentDialogContent = ({
  onClose,
  form,
  balance,
  debt,
  debtType,
}: DebtRepaymentDialogContentProps) => {
  const { t } = useTranslation()
  const { mutation: stepMutation } = useStepper()

  const mutation = useDebtRepaymentDialog({
    balance,
    values: form.value,
    onClose,
    debtType,
  })

  return (
    <DebitOperationStepperDialog
      onClose={onClose}
      balance={balance}
      title={t("Acquittement de dette")}
      submitLabel={t("Valider l'acquittement de dette")}
      form={form}
      formId="debt-repayment-dialog"
      mutation={mutation}
      notice={
        <>
          <DebtRemainingNotice
            debt={debt}
            debtType={debtType}
            simulation={form.value.simulation}
          />
          {debtType === DebtType.TCO2 && mutation.error && (
            <Alert
              severity="error"
              small
              description={t(
                "Le remboursement n'a pas été enregistré. Revenez aux filtres pour actualiser le calcul avant de réessayer."
              )}
            />
          )}
        </>
      }
      renderSummaries={(currentStepIndex) => (
        <>
          {currentStepIndex > 2 &&
            (debtType === DebtType.TCO2 ? (
              <>
                <OperationText
                  title={t("Volume à prélever")}
                  description={formatAccountingUnit(
                    form.value.simulation?.total_volume ?? 0,
                    Unit.l
                  )}
                />
                <OperationText
                  title={t("Dette acquittée")}
                  description={formatDebtTco2(
                    form.value.simulation
                      ? form.value.simulation.debt_tco2 -
                          form.value.simulation.remaining_tco2
                      : 0
                  )}
                />
                <OperationText
                  title={t("Dette restant à acquitter")}
                  description={formatDebtTco2(
                    form.value.simulation?.remaining_tco2 ?? 0
                  )}
                />
              </>
            ) : (
              <QuantitySummary values={form.value} />
            ))}
        </>
      )}
      renderStepContent={(currentStepKey) => (
        <>
          {currentStepKey === DEBT_REPAYMENT_FILTERS_STEP_KEY && (
            <fieldset
              disabled={stepMutation.loading}
              style={{ border: 0, padding: 0, margin: 0, minWidth: 0 }}
            >
              <AdvancedFiltersBalanceCard initialBalance={balance} />
            </fieldset>
          )}
          {currentStepKey === DEBT_REPAYMENT_TCO2_STEP_KEY && (
            <DebtRepaymentTco2Summary simulation={form.value.simulation} />
          )}
          {currentStepKey === quantityFormStepKey && (
            <Box>
              <QuantityForm
                balance={balance}
                quantityMax={getDebtRepaymentMaxQuantity(
                  debt,
                  form.value.availableBalance ?? 0
                )}
                type={CreateOperationType.DEBT_REPAYMENT}
              />
            </Box>
          )}
        </>
      )}
    />
  )
}
