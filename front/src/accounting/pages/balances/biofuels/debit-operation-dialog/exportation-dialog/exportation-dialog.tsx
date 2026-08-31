import {
  FromDepotFiltersForm,
  fromDepotFiltersStep,
  fromDepotFiltersStepKey,
  FromDepotFiltersSummary,
} from "../components/from-depot-filters-form"
import { Balance, CreateOperationType } from "accounting/types"
import { FormManager, useForm } from "common/components/form2"
import { Box } from "common/components/scaffold"
import { StepperProvider } from "common/components/stepper"
import { useTranslation } from "react-i18next"
import {
  CountryForm,
  countryFormStep,
  countryFormStepKey,
  CountryFormSummary,
} from "./country-form"
import { ExportationDialogForm } from "./exportation-dialog.types"
import { useExportationDialog } from "./exportation-dialog.hooks"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import { DebitOperationStepperDialog } from "../components/debit-operation-stepper-dialog"

interface ExportationDialogProps {
  onClose: () => void
  onOperationCreated: () => void
  balance: Balance
}
interface ExportationDialogContentProps extends ExportationDialogProps {
  form: FormManager<ExportationDialogForm>
}

export const ExportationDialogContent = ({
  onClose,
  form,
  balance,
  onOperationCreated,
}: ExportationDialogContentProps) => {
  const { t } = useTranslation()

  const mutation = useExportationDialog({
    balance,
    values: form.value,
    onClose,
    onOperationCreated,
  })

  return (
    <DebitOperationStepperDialog
      onClose={onClose}
      balance={balance}
      title={t("Réaliser une exportation")}
      submitLabel={t("Exporter")}
      form={form}
      formId="exportation-dialog"
      mutation={mutation}
      renderSummaries={(currentStepIndex) => (
        <>
          {currentStepIndex > 1 && (
            <FromDepotFiltersSummary values={form.value} />
          )}
          {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
          {currentStepIndex > 3 && <CountryFormSummary values={form.value} />}
        </>
      )}
      renderStepContent={(currentStepKey) => (
        <>
          {currentStepKey === fromDepotFiltersStepKey && (
            <FromDepotFiltersForm balance={balance} />
          )}
          {currentStepKey === quantityFormStepKey && (
            <Box>
              <QuantityForm
                balance={balance}
                quantityMax={form.value.availableBalance ?? 0}
                type={CreateOperationType.EXPORTATION}
              />
            </Box>
          )}
          {currentStepKey === countryFormStepKey && (
            <Box>
              <CountryForm />
            </Box>
          )}
        </>
      )}
    />
  )
}

export const ExportationDialog = (props: ExportationDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<ExportationDialogForm>({})
  const exportationQuantityFormStep = useQuantityFormStep({
    balance: props.balance,
    form,
    overrides: {
      title: t(
        "Quantité d'énergie exportée et tonnes de CO2 évitées équivalentes"
      ),
    },
  })

  const steps = [
    fromDepotFiltersStep(form.value),
    exportationQuantityFormStep,
    countryFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]

  return (
    <StepperProvider steps={steps}>
      <ExportationDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
