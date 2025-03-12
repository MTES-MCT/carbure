import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Balance, CreateOperationType } from "accounting/types"
import { Trans, useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import {
  FromDepotForm,
  FromDepotSummary,
  fromDepotStep,
  fromDepotStepKey,
} from "accounting/components/from-depot-form"
import { useForm, Form, FormManager } from "common/components/form2"
import { SessionDialogForm } from "./cession-dialog.types"
import { Button } from "common/components/button2"
import {
  QuantityForm,
  QuantitySummary,
  quantityFormStep,
  quantityFormStepKey,
} from "accounting/components/quantity-form"
import {
  RecipientToDepotForm,
  recipientToDepotStep,
  recipientToDepotStepKey,
  RecipientToDepotSummary,
} from "accounting/components/recipient-to-depot-form"
import { RecapOperation } from "accounting/components/recap-operation"

import { useCessionDialog } from "./cession-dialog.hooks"

interface CessionDialogProps {
  onClose: () => void
  onOperationCreated: () => void
  balance: Balance
}

interface CessionDialogContentProps extends CessionDialogProps {
  form: FormManager<SessionDialogForm>
}
export const CessionDialogContent = ({
  onClose,
  onOperationCreated,
  balance,
  form,
}: CessionDialogContentProps) => {
  const { t } = useTranslation()

  const { currentStep, currentStepIndex } = useStepper()

  const mutation = useCessionDialog({
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
            <Trans>Réaliser une cession</Trans>
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
                {t("Céder")}
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
                type={CreateOperationType.CESSION}
              />
            )}
            {currentStepIndex > 3 && form.value.credited_entity && (
              <RecipientToDepotSummary values={form.value} />
            )}
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
                    type={CreateOperationType.CESSION}
                  />
                )}
                {currentStep?.key === recipientToDepotStepKey && (
                  <RecipientToDepotForm />
                )}
              </Form>
            </Box>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}

export const CessionDialog = (props: CessionDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<SessionDialogForm>({})
  const steps = [
    fromDepotStep(form.value),
    quantityFormStep(form.value),
    recipientToDepotStep(form.value),
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <CessionDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
