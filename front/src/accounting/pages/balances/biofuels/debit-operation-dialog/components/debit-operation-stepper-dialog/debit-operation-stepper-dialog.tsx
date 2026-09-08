import { Dialog } from "common/components/dialog2"
import { Button } from "common/components/button2"
import { Box, Main } from "common/components/scaffold"
import { Stepper, useStepper } from "common/components/stepper"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import { Balance } from "accounting/types"
import { FormManager } from "common/components/form2"
import { ReactNode } from "react"
import { useTranslation } from "react-i18next"

// Key shared by every debit operation dialog for the last (recap) step
export const RECAP_STEP_KEY = "recap"

type DebitOperationMutation = {
  execute: (args?: { draft?: boolean }) => unknown
  loading: boolean
}

type DebitOperationStepperDialogProps<T> = {
  onClose: () => void
  balance: Balance
  title: ReactNode
  submitLabel: ReactNode
  form: FormManager<T>
  formId: string
  mutation: DebitOperationMutation

  // Summaries displayed in the recap grid, based on the current step index
  renderSummaries: (currentStepIndex: number) => ReactNode

  // Content of the current step, based on the current step key
  renderStepContent: (currentStepKey: string) => ReactNode
}

// Shared layout (dialog, stepper, recap grid, footer actions) used by every
// debit operation dialog (transfert, exportation, devaluation, ...)
export const DebitOperationStepperDialog = <T,>({
  onClose,
  balance,
  title,
  submitLabel,
  form,
  formId,
  mutation,
  renderSummaries,
  renderStepContent,
}: DebitOperationStepperDialogProps<T>) => {
  const { t } = useTranslation()
  const { currentStep, currentStepIndex } = useStepper()
  const isRecapStep = currentStep?.key === RECAP_STEP_KEY

  return (
    <Dialog
      fullWidth
      onClose={onClose}
      header={<Dialog.Title>{title}</Dialog.Title>}
      footer={
        <>
          <Stepper.Previous />
          <Stepper.Next nativeButtonProps={{ form: formId }} />
          {isRecapStep && (
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
                {submitLabel}
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
            <RecapOperation balance={balance} />
            {renderSummaries(currentStepIndex)}
          </RecapOperationGrid>
        </Box>

        {!isRecapStep && (
          <Stepper.Form form={form} id={formId}>
            {renderStepContent(currentStep?.key)}
          </Stepper.Form>
        )}
      </Main>
    </Dialog>
  )
}
