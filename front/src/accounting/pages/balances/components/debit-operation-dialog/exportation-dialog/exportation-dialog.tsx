import {
  FromDepotForm,
  fromDepotStep,
  fromDepotStepKey,
  FromDepotSummary,
} from "accounting/components/from-depot-form"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import { Balance } from "accounting/types"
import Dialog from "common/components/dialog2/dialog"
import { Form, FormManager, useForm } from "common/components/form2"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { Trans, useTranslation } from "react-i18next"
import {
  CountryForm,
  countryFormStep,
  countryFormStepKey,
  CountryFormSummary,
} from "./country-form"
import { Button } from "common/components/button2"
import { ExportationDialogForm } from "./exportation-dialog.types"
import { useExportationDialog } from "./exportation-dialog.hooks"
import {
  ExportationQuantityForm,
  exportationQuantityFormStep,
  exportationQuantityFormStepKey,
  ExportationQuantitySummary,
} from "./exportation-quantity-form"

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
  const { currentStep, currentStepIndex } = useStepper()
  const { t } = useTranslation()

  const mutation = useExportationDialog({
    balance,
    values: form.value,
    onClose,
    onOperationCreated,
  })
  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={
          <Dialog.Title>
            <Trans>Réaliser une exportation</Trans>
          </Dialog.Title>
        }
        footer={
          <>
            <Stepper.Previous />
            <Stepper.Next />
            {currentStep?.key === "recap" && (
              <Button
                priority="primary"
                onClick={() => mutation.execute()}
                loading={mutation.loading}
              >
                {t("Déclarer une exportation")}
              </Button>
            )}
          </>
        }
      >
        <Main>
          <Stepper />
          <Box>
            <RecapOperationGrid>
              <RecapOperation balance={balance} />
              {currentStepIndex > 1 && <FromDepotSummary values={form.value} />}
              {currentStepIndex > 2 && (
                <ExportationQuantitySummary values={form.value} />
              )}
              {currentStepIndex > 3 && (
                <CountryFormSummary values={form.value} />
              )}
            </RecapOperationGrid>
          </Box>
          {currentStep?.key !== "recap" && (
            <Box>
              <Form form={form}>
                {currentStep?.key === fromDepotStepKey && (
                  <FromDepotForm balance={balance} />
                )}
                {currentStep?.key === exportationQuantityFormStepKey && (
                  <ExportationQuantityForm
                    balance={balance}
                    depot_quantity_max={form.value.from_depot?.quantity.credit}
                  />
                )}
                {currentStep?.key === countryFormStepKey && <CountryForm />}
              </Form>
            </Box>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}

export const ExportationDialog = (props: ExportationDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<ExportationDialogForm>({})

  const steps = [
    fromDepotStep(form.value),
    exportationQuantityFormStep(form.value),
    countryFormStep(form.value),
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <ExportationDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
