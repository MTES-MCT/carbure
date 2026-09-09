import { Balance, CreateOperationType } from "accounting/types"
import { Box } from "common/components/scaffold"
import { FormManager, useForm } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { StepperProvider } from "common/components/stepper"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import {
  FromDepotFiltersForm,
  fromDepotFiltersStep,
  fromDepotFiltersStepKey,
  FromDepotFiltersSummary,
} from "../components/from-depot-filters-form"
import { DebitOperationStepperDialog } from "../components/debit-operation-stepper-dialog"
import { DevaluationDialogForm } from "./devaluation-dialog.types"
import { useDevaluationDialog } from "./devaluation-dialog.hooks"
import {
  DevaluationTypeForm,
  DevaluationTypeSummary,
} from "./devaluation-type-form"

interface DevaluationDialogProps {
  onClose: () => void
  onOperationCreated: () => void
  balance: Balance
}

interface DevaluationDialogContentProps extends DevaluationDialogProps {
  form: FormManager<DevaluationDialogForm>
}

export const DevaluationDialogContent = ({
  onClose,
  onOperationCreated,
  balance,
  form,
}: DevaluationDialogContentProps) => {
  const { t } = useTranslation()

  const mutation = useDevaluationDialog({
    balance,
    values: form.value,
    onClose,
    onOperationCreated,
  })

  return (
    <DebitOperationStepperDialog
      onClose={onClose}
      balance={balance}
      title={t("Réaliser une dévalorisation")}
      submitLabel={t("Dévaloriser")}
      form={form}
      formId="devaluation-dialog"
      mutation={mutation}
      renderSummaries={(currentStepIndex) => (
        <>
          {currentStepIndex > 1 && (
            <>
              <DevaluationTypeSummary values={form.value} />
              <FromDepotFiltersSummary values={form.value} />
            </>
          )}
          {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
        </>
      )}
      renderStepContent={(currentStepKey) => (
        <>
          {currentStepKey === fromDepotFiltersStepKey && (
            <FromDepotFiltersForm balance={balance}>
              <DevaluationTypeForm />
            </FromDepotFiltersForm>
          )}
          {currentStepKey === quantityFormStepKey && (
            <Box>
              <QuantityForm
                balance={balance}
                quantityMax={form.value.availableBalance ?? 0}
                type={CreateOperationType.DEVALUATION}
              />
            </Box>
          )}
        </>
      )}
    />
  )
}

export const DevaluationDialog = (props: DevaluationDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<DevaluationDialogForm>({})
  const devaluationQuantityFormStep = useQuantityFormStep({
    balance: props.balance,
    form,
    overrides: {
      title: t(
        "Quantité d'énergie dévalorisée et tonnes de CO2 évitées équivalentes"
      ),
    },
  })

  const steps = [
    fromDepotFiltersStep(form.value, {
      title: t("Type de dévalorisation, dépôt et filtres"),
    }),
    devaluationQuantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]

  return (
    <StepperProvider steps={steps}>
      <DevaluationDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
