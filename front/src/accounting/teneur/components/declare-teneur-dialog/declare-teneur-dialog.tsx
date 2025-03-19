import Dialog from "common/components/dialog2/dialog"
import { useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { FormManager, useForm, Form } from "common/components/form2"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import {
  QuantityForm,
  quantityFormStep,
  quantityFormStepKey,
} from "accounting/components/quantity-form"
import { Box, Main } from "common/components/scaffold"
import {
  BiofuelForm,
  biofuelFormStep,
  biofuelFormStepKey,
} from "./biofuel-form"
import { CategoryEnum, ExtendedUnit, Unit } from "common/types"
import { CreateOperationType } from "accounting/types"
import { Text } from "common/components/text"
import { ProgressBar } from "../progress-bar"
import { RecapData } from "../recap-data"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"

interface DeclareTeneurDialogProps {
  onClose: () => void
}

interface DeclareTeneurDialogContentProps extends DeclareTeneurDialogProps {
  form: FormManager<DeclareTeneurDialogForm>
}

const DeclareTeneurDialogContent = ({
  onClose,
  form,
}: DeclareTeneurDialogContentProps) => {
  const { t } = useTranslation()
  const { currentStep, currentStepIndex } = useStepper()

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>{t("J'alimente ma teneur mensuelle")}</Dialog.Title>
      }
      footer={
        <>
          <Stepper.Previous />
          <Stepper.Next />
        </>
      }
      fullWidth
    >
      <Main>
        <Stepper />
        {currentStep?.key !== biofuelFormStepKey && (
          <>
            <Box gap="xs">
              <Text>{t("Rappel de votre progression")}</Text>
              <ProgressBar
                baseQuantity={0}
                targetQuantity={100}
                declaredQuantity={50}
              />
              {/* TODO: conditionner les phrases à afficher selon le type de catégorie */}
              <RecapData.RemainingQuantityBeforeLimit
                value={100}
                unit={ExtendedUnit.GJ}
              />
            </Box>
            <Box>
              <RecapOperationGrid>
                <RecapOperation
                  balance={form.value.balance!}
                  unit={ExtendedUnit.GJ}
                />
              </RecapOperationGrid>
            </Box>
          </>
        )}
        {currentStep?.key !== "recap" && (
          <Box>
            <Form form={form}>
              {currentStep?.key === biofuelFormStepKey && <BiofuelForm />}
              {currentStep?.key === quantityFormStepKey && (
                <QuantityForm
                  balance={form.value.balance!}
                  type={CreateOperationType.TENEUR}
                  depot_quantity_max={form.value.balance?.available_balance}
                  unit={ExtendedUnit.GJ}
                />
              )}
            </Form>
          </Box>
        )}
      </Main>
    </Dialog>
  )
}

export const DeclareTeneurDialog = (props: DeclareTeneurDialogProps) => {
  const { t } = useTranslation()
  const form = useForm<DeclareTeneurDialogForm>({})
  const steps = [
    biofuelFormStep(form.value),
    quantityFormStep(form.value, {
      title: t("Quantité de la teneur et tC02 évitées"),
    }),
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <DeclareTeneurDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
