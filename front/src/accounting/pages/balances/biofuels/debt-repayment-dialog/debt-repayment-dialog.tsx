import { AdvancedFiltersBalanceCard } from "accounting/components/advanced-filters/advanced-filters"
import { showNextStepAdvancedFilters } from "accounting/components/advanced-filters/advanced-filters.utils"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import { Balance, CreateOperationType, Debt } from "accounting/types"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { getDebtRepaymentMaxQuantity } from "accounting/utils/debts"
import { FormManager, useForm } from "common/components/form2"
import { Notice } from "common/components/notice"
import { Box } from "common/components/scaffold"
import { StepperProvider } from "common/components/stepper"
import { Unit } from "common/types"
import { Trans, useTranslation } from "react-i18next"
import { DebitOperationStepperDialog } from "../debit-operation-dialog/components/debit-operation-stepper-dialog"
import { useDebtRepaymentDialog } from "./debt-repayment-dialog.hooks"
import { DebtRepaymentDialogForm } from "./debt-repayment-dialog.types"

const filtersStepKey = "debt-repayment-filters"

interface DebtRepaymentDialogProps {
  onClose: () => void
  balance: Balance
  debt: Debt
}
interface DebtRepaymentDialogContentProps extends DebtRepaymentDialogProps {
  form: FormManager<DebtRepaymentDialogForm>
}

const DebtRemainingNotice = ({ debt }: { debt: Debt }) => {
  const { t } = useTranslation()

  return (
    <Notice noColor variant="info">
      <Trans
        components={{ b: <b /> }}
        t={t}
        values={{
          volume: formatAccountingUnit(debt.remaining_volume, Unit.l),
        }}
        defaults="Vous devez <b>{{volume}}</b>"
      />
    </Notice>
  )
}

export const DebtRepaymentDialogContent = ({
  onClose,
  form,
  balance,
  debt,
}: DebtRepaymentDialogContentProps) => {
  const { t } = useTranslation()

  const mutation = useDebtRepaymentDialog({
    balance,
    values: form.value,
    onClose,
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
      notice={<DebtRemainingNotice debt={debt} />}
      renderSummaries={(currentStepIndex) => (
        <>{currentStepIndex > 2 && <QuantitySummary values={form.value} />}</>
      )}
      renderStepContent={(currentStepKey) => (
        <>
          {currentStepKey === filtersStepKey && (
            <AdvancedFiltersBalanceCard initialBalance={balance} />
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

export const DebtRepaymentDialog = (props: DebtRepaymentDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<DebtRepaymentDialogForm>({})
  const quantityStep = useQuantityFormStep({
    balance: props.balance,
    form,
    overrides: {
      title: t(
        "Quantité d'énergie acquittée et tonnes de CO2 évitées équivalentes"
      ),
    },
  })

  const steps = [
    {
      key: filtersStepKey,
      title: t("Filtres"),
      allowNextStep: showNextStepAdvancedFilters(form.value),
    },
    quantityStep,
    { key: "recap", title: t("Récapitulatif") },
  ]

  return (
    <StepperProvider steps={steps}>
      <DebtRepaymentDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
