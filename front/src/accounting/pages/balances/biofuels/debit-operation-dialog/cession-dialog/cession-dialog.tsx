import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Box, Main } from "common/components/scaffold"
import { Balance, CreateOperationType } from "accounting/types"
import { Trans, useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { useForm, Form, FormManager } from "common/components/form2"
import { SessionDialogForm } from "./cession-dialog.types"
import { Button } from "common/components/button2"
import {
  QuantityForm,
  QuantitySummary,
  quantityFormStepKey,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"

import { useCessionDialog } from "./cession-dialog.hooks"
import {
  fromDepotRecipientToDepotStep,
  fromDepotRecipientToDepotStepKey,
  FromDepotRecipientToDepotSummary,
} from "./from-depot-recipient-to-depot-form/from-depot-recipient-to-depot-form"
import { FromDepotForm } from "accounting/components/from-depot-form"
import { RecipientToDepotForm } from "accounting/components/recipient-to-depot-form"
import { RecapGHGRange } from "accounting/components/recap-ghg-range/recap-ghg-range"

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
            <RecapOperationGrid>
              <RecapOperation balance={balance} />
              {currentStepIndex > 1 && (
                <>
                  <FromDepotRecipientToDepotSummary values={form.value} />
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
              {currentStep?.key === fromDepotRecipientToDepotStepKey && (
                <>
                  <Box>
                    <RecipientToDepotForm />
                  </Box>
                  <Box>
                    <FromDepotForm balance={balance} />
                  </Box>
                </>
              )}
              {currentStep?.key === quantityFormStepKey && (
                <Box>
                  <QuantityForm
                    balance={balance}
                    depot_quantity_max={
                      form.value.from_depot?.available_balance
                    }
                    type={CreateOperationType.CESSION}
                    depotId={form.value.from_depot?.id}
                    gesBoundMin={form.value.gesBoundMin}
                    gesBoundMax={form.value.gesBoundMax}
                  />
                </Box>
              )}
            </Form>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}

export const CessionDialog = (props: CessionDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<SessionDialogForm>({})
  const quantityFormStep = useQuantityFormStep({
    balance: props.balance,
    form,
  })
  const steps = [
    fromDepotRecipientToDepotStep(form.value),
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <CessionDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
