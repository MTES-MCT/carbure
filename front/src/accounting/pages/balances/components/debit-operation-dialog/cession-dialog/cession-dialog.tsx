import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { Main } from "common/components/scaffold"
import { Balance } from "accounting/types"
import { Trans, useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import {
  FromDepotForm,
  FromDepotSummary,
  fromDepotStep,
  fromDepotStepKey,
} from "accounting/components/from-depot-form"
import styles from "./cession-dialog.module.css"
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

  const { currentStep, currentStepIndex, previousStep, nextStep } = useStepper()

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
            {previousStep && <Stepper.Previous />}
            {nextStep && <Stepper.Next />}
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
          <RecapOperation balance={balance} />
          {currentStepIndex > 1 && <FromDepotSummary values={form.value} />}
          {currentStepIndex > 2 && <QuantitySummary values={form.value} />}
          {currentStepIndex > 3 && form.value.credited_entity && (
            <RecipientToDepotSummary values={form.value} />
          )}
          {currentStep?.key !== "recap" && (
            <div className={styles["cession-dialog__form"]}>
              <Form form={form}>
                {currentStep?.key === fromDepotStepKey && (
                  <FromDepotForm balance={balance} />
                )}
                {currentStep?.key === quantityFormStepKey && (
                  <QuantityForm
                    balance={balance}
                    depot_quantity_max={form.value.from_depot?.quantity.credit}
                  />
                )}
                {currentStep?.key === recipientToDepotStepKey && (
                  <RecipientToDepotForm />
                )}
              </Form>
            </div>
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
