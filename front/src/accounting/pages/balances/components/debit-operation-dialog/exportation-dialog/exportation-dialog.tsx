import {
  FromDepotForm,
  FromDepotFormProps,
  fromDepotStep,
  fromDepotStepKey,
  FromDepotSummary,
} from "accounting/components/from-depot-form"
import {
  QuantityForm,
  QuantityFormProps,
  quantityFormStep,
  quantityFormStepKey,
  QuantitySummary,
} from "accounting/components/quantity-form"
import { RecapOperation } from "accounting/components/recap-operation"
import { Balance, CreateOperationType } from "accounting/types"
import Dialog from "common/components/dialog2/dialog"
import { Form, FormManager, useForm } from "common/components/form2"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { Trans, useTranslation } from "react-i18next"
import {
  CountryForm,
  CountryFormProps,
  countryFormStep,
  countryFormStepKey,
  CountryFormSummary,
} from "./country-form"
import { Button } from "common/components/button2"

type ExportationDialogForm = FromDepotFormProps &
  QuantityFormProps &
  CountryFormProps
interface ExportationDialogProps {
  onClose: () => void
  balance: Balance
}
interface ExportationDialogContentProps extends ExportationDialogProps {
  form: FormManager<ExportationDialogForm>
}

export const ExportationDialogContent = ({
  onClose,
  form,
  balance,
}: ExportationDialogContentProps) => {
  const { currentStep, currentStepIndex } = useStepper()
  const { t } = useTranslation()
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
              <Button priority="primary" onClick={() => {}}>
                {t("Déclarer une exportation")}
              </Button>
            )}
          </>
        }
      >
        <Main>
          <Stepper />
          <Box>
            <RecapOperation balance={balance} />
            {currentStepIndex > 1 && <FromDepotSummary values={form.value} />}
            {currentStepIndex > 2 && (
              <QuantitySummary
                values={form.value}
                type={CreateOperationType.EXPORTATION}
              />
            )}
            {currentStepIndex > 3 && <CountryFormSummary values={form.value} />}
          </Box>
          {currentStep?.key !== "recap" && (
            <Box>
              <Form form={form}>
                {currentStep?.key === fromDepotStepKey && (
                  <FromDepotForm balance={balance} />
                )}
                {currentStep?.key === quantityFormStepKey && (
                  <QuantityForm
                    balance={balance}
                    depot_quantity_max={form.value.from_depot?.quantity.credit}
                    type={CreateOperationType.EXPORTATION}
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
    quantityFormStep(form.value),
    countryFormStep(form.value),
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <ExportationDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
