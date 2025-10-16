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
import { Balance, CreateOperationType } from "accounting/types"
import Dialog from "common/components/dialog2/dialog"
import { FormManager, useForm } from "common/components/form2"
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
import { RecapGHGRange } from "accounting/components/recap-ghg-range/recap-ghg-range"
import { GHGRangeForm } from "accounting/components/ghg-range-form"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"

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

  // Change the available balance value only if the GHG range step is completed
  const currentBalance =
    currentStepIndex > 1
      ? {
          ...balance,
          available_balance: form.value.availableBalance!,
        }
      : balance
  return (
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
          <Stepper.Next nativeButtonProps={{ form: "exportation-dialog" }} />
          {currentStep?.key === "recap" && (
            <>
              <Button
                priority="secondary"
                onClick={() => mutation.execute({ draft: true })}
                loading={mutation.loading}
              >
                {t("Sauvegarder")}
              </Button>

              <Button
                priority="primary"
                onClick={() => mutation.execute({ draft: false })}
                loading={mutation.loading}
              >
                {t("Exporter")}
              </Button>
            </>
          )}
        </>
      }
    >
      <Main>
        <Stepper />
        <Box>
          <RecapOperationGrid>
            <RecapOperation balance={currentBalance} />
            {currentStepIndex > 1 && (
              <>
                <FromDepotSummary values={form.value} />
                <RecapGHGRange
                  min={form.value.gesBoundMin}
                  max={form.value.gesBoundMax}
                />
              </>
            )}
            {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
            {currentStepIndex > 3 && <CountryFormSummary values={form.value} />}
          </RecapOperationGrid>
        </Box>
        {currentStep?.key !== "recap" && (
          <Stepper.Form form={form} id="exportation-dialog">
            {currentStep?.key === fromDepotStepKey && (
              <>
                <Box>
                  <FromDepotForm />
                </Box>
                <Box>
                  <GHGRangeForm balance={balance} />
                </Box>
              </>
            )}
            {currentStep?.key === quantityFormStepKey && (
              <Box>
                <QuantityForm
                  balance={balance}
                  quantityMax={form.value.availableBalance}
                  type={CreateOperationType.EXPORTATION}
                  gesBoundMin={form.value.gesBoundMin}
                  gesBoundMax={form.value.gesBoundMax}
                />
              </Box>
            )}
            {currentStep?.key === countryFormStepKey && (
              <Box>
                <CountryForm />
              </Box>
            )}
          </Stepper.Form>
        )}
      </Main>
    </Dialog>
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
    fromDepotStep,
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
