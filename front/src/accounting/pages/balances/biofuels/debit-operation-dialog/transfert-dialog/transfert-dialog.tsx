import { Balance, CreateOperationType } from "accounting/types"
import { Dialog } from "common/components/dialog2"
import { Form, FormManager, useForm } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { TransfertDialogForm } from "./transfert-dialog.types"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import {
  RecipientToDepotForm,
  recipientToDepotStep,
  recipientToDepotStepKey,
  RecipientToDepotSummary,
} from "accounting/components/recipient-to-depot-form"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { useTransfertDialog } from "./transfert-dialog.hooks"
import { Button } from "common/components/button2"
import { Box, Main } from "common/components/scaffold"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import { RecapGHGRange } from "accounting/components/recap-ghg-range/recap-ghg-range"
import { TransfertGHGRangeForm } from "./ghg-range-form"

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

  const { currentStep, currentStepIndex } = useStepper()

  const mutation = useTransfertDialog({
    balance,
    values: form.value,
    onClose,
    onOperationCreated,
  })

  return (
    <Dialog
      fullWidth
      onClose={onClose}
      header={
        <Dialog.Title>{t("Réaliser un transfert de droits")}</Dialog.Title>
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
              {t("Transférer")}
            </Button>
          )}
        </>
      }
    >
      <Main>
        <Stepper />
        <Box>
          <RecapOperationGrid>
            <RecapOperation
              balance={
                // Change the available balance value only if the step is completed
                currentStepIndex > 1
                  ? {
                      ...balance,
                      available_balance:
                        form.value.availableBalance ??
                        balance.available_balance,
                    }
                  : balance
              }
            />
            {currentStepIndex > 1 && (
              <>
                <RecipientToDepotSummary values={form.value} />
                <RecapGHGRange
                  min={form.value.gesBoundMin}
                  max={form.value.gesBoundMax}
                />
              </>
            )}
            {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
          </RecapOperationGrid>
        </Box>

        {currentStep?.key !== "recap" && (
          <Form form={form}>
            {currentStep?.key === recipientToDepotStepKey && (
              <>
                <Box>
                  <RecipientToDepotForm />
                </Box>
                <Box>
                  <TransfertGHGRangeForm balance={balance} />
                </Box>
              </>
            )}
            {currentStep?.key === quantityFormStepKey && (
              <Box>
                <QuantityForm
                  balance={balance}
                  depot_quantity_max={
                    form.value.availableBalance ?? balance.available_balance
                  }
                  type={CreateOperationType.TRANSFERT}
                  gesBoundMin={form.value.gesBoundMin}
                  gesBoundMax={form.value.gesBoundMax}
                />
              </Box>
            )}
          </Form>
        )}
      </Main>
    </Dialog>
  )
}

export const TransfertDialog = (props: TransfertDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<TransfertDialogForm>({
    gesBoundMin: Math.floor(props.balance.ghg_reduction_min),
    gesBoundMax: Math.ceil(props.balance.ghg_reduction_max),
    availableBalance: props.balance.available_balance,
  })
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
    recipientToDepotStep(form.value),
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <TransfertDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
