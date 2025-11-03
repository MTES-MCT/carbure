import { Balance, CreateOperationType } from "accounting/types"
import { Dialog } from "common/components/dialog2"
import { FormManager, useForm } from "common/components/form2"
import { useTranslation } from "react-i18next"
import { TransfertDialogForm } from "./transfert-dialog.types"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { useTransfertDialog } from "./transfert-dialog.hooks"
import { Button } from "common/components/button2"
import { Box, Main } from "common/components/scaffold"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import {
  RecipientForm,
  recipientStep,
  recipientStepKey,
  RecipientSummary,
} from "accounting/components/recipient-form"
import { GHGRangeForm } from "accounting/components/ghg-range-form"

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
        <Dialog.Title>{t("Réaliser un transfert de droits")}</Dialog.Title>
      }
      footer={
        <>
          <Stepper.Previous />
          <Stepper.Next nativeButtonProps={{ form: "transfert-dialog" }} />
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
                {t("Transférer")}
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
            {currentStepIndex > 1 && <RecipientSummary values={form.value} />}
            {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
          </RecapOperationGrid>
        </Box>

        {currentStep?.key !== "recap" && (
          <Stepper.Form form={form} id="transfert-dialog">
            {currentStep?.key === recipientStepKey && (
              <>
                <Box>
                  <RecipientForm />
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
                  quantityMax={form.value.availableBalance ?? 0}
                  type={CreateOperationType.TRANSFERT}
                  gesBoundMin={form.value.gesBoundMin}
                  gesBoundMax={form.value.gesBoundMax}
                />
              </Box>
            )}
          </Stepper.Form>
        )}
      </Main>
    </Dialog>
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
    recipientStep,
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <TransfertDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
