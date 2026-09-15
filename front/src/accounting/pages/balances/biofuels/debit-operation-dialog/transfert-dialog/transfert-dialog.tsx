import { Balance, CreateOperationType } from "accounting/types"
import { FormManager, useForm } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { TransfertDialogForm } from "./transfert-dialog.types"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import { StepperProvider } from "common/components/stepper"
import { useTransfertDialog } from "./transfert-dialog.hooks"
import { Box } from "common/components/scaffold"
import { DebitOperationStepperDialog } from "../components/debit-operation-stepper-dialog"

import {
  RecipientFiltersForm,
  recipientFiltersStep,
  recipientFiltersStepKey,
  RecipientFiltersSummary,
} from "./recipient-filters-form"

interface TransfertDialogProps {
  onClose: () => void
  onOperationCreated: () => void
  balance: Balance
}

interface TransfertDialogContentProps extends TransfertDialogProps {
  form: FormManager<TransfertDialogForm>
}

export const TransfertDialogContent = ({
  onClose,
  onOperationCreated,
  balance,
  form,
}: TransfertDialogContentProps) => {
  const { t } = useTranslation()

  const mutation = useTransfertDialog({
    balance,
    values: form.value,
    onClose,
    onOperationCreated,
  })

  return (
    <DebitOperationStepperDialog
      onClose={onClose}
      balance={balance}
      title={t("Réaliser un transfert de droits")}
      submitLabel={t("Transférer")}
      form={form}
      formId="transfert-dialog"
      mutation={mutation}
      renderSummaries={(currentStepIndex) => (
        <>
          {currentStepIndex > 1 && (
            <RecipientFiltersSummary values={form.value} />
          )}
          {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
        </>
      )}
      renderStepContent={(currentStepKey) => (
        <>
          {currentStepKey === recipientFiltersStepKey && (
            <RecipientFiltersForm balance={balance} />
          )}
          {currentStepKey === quantityFormStepKey && (
            <Box>
              <QuantityForm
                balance={balance}
                quantityMax={form.value.availableBalance ?? 0}
                type={CreateOperationType.TRANSFERT}
              />
            </Box>
          )}
        </>
      )}
    />
  )
}

export const TransfertDialog = (props: TransfertDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<TransfertDialogForm>({})
  const quantityFormStep = useQuantityFormStep({
    balance: props.balance,
    form,
    overrides: {
      title: t(
        "Quantité d'énergie transférée et tonnes de CO2 évitées équivalentes"
      ),
    },
  })

  const steps = [
    recipientFiltersStep(form.value),
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <TransfertDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
