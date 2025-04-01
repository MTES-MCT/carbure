import Dialog from "common/components/dialog2/dialog"
import { useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { FormManager, useForm, Form } from "common/components/form2"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import {
  QuantityForm,
  quantityFormStep,
  quantityFormStepKey,
  QuantitySummary,
} from "accounting/components/quantity-form"
import { Box, Main } from "common/components/scaffold"
import {
  BiofuelForm,
  biofuelFormStep,
  biofuelFormStepKey,
} from "./biofuel-form"
import { ExtendedUnit, Unit } from "common/types"
import { CreateOperationType } from "accounting/types"
import { Text } from "common/components/text"
import { ProgressBar } from "../progress-bar"
import { RecapData } from "../recap-data"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import {
  CategoryObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../types"
import { ceilNumber, CONVERSIONS, floorNumber } from "common/utils/formatters"
import { computeObjectiveEnergy, formatEnergy } from "../../utils/formatters"
import { useMemo } from "react"
import { Button } from "common/components/button2"
import { useDeclareTeneurDialog } from "./declare-teneur-dialog.hooks"

interface DeclareTeneurDialogProps {
  onClose: () => void
  objective: CategoryObjective | UnconstrainedCategoryObjective
  targetType?: TargetType
}

interface DeclareTeneurDialogContentProps extends DeclareTeneurDialogProps {
  form: FormManager<DeclareTeneurDialogForm>
}

const DeclareTeneurDialogContent = ({
  onClose,
  form,
  objective,
  targetType,
}: DeclareTeneurDialogContentProps) => {
  const { t } = useTranslation()
  const { currentStep, currentStepIndex } = useStepper()
  const mutation = useDeclareTeneurDialog({
    onClose,
    onOperationCreated: () => {},
    values: form.value,
  })

  const formatNumber =
    targetType && targetType === TargetType.REACH ? ceilNumber : floorNumber

  const remainingEnergyBeforeLimitOrObjective = useMemo(() => {
    // Add quantity declared only if the "declare quantity" button has been clicked
    const quantity = form.value.quantity ?? 0

    const remainingEnergy = Math.max(
      0,
      objective.target
        ? computeObjectiveEnergy(objective) -
            CONVERSIONS.energy.GJ_TO_MJ(quantity)
        : 0
    )

    return formatEnergy(remainingEnergy, {
      unit: ExtendedUnit.GJ,
      fractionDigits: 0,
      // If the target is a reach, we need to ceil the remaining energy
      // Ex: if the remaining energy to declare is 145.88 GJ, we need to declare 146 GJ
      // because the objective is to reach a certain quantity
      mode: targetType === TargetType.REACH ? "ceil" : "floor",
    })
  }, [form.value.quantity, objective, targetType])

  // Define the maximum quantity that can be declared for the teneur
  // If a target is defined, the maximum quantity is the minimum between the available balance and the objective
  // Otherwise, the maximum quantity is the available balance
  const depotQuantityMax = formatNumber(
    form.value.balance
      ? objective.target
        ? Math.min(
            CONVERSIONS.energy.MJ_TO_GJ(form.value.balance!.available_balance),
            CONVERSIONS.energy.MJ_TO_GJ(computeObjectiveEnergy(objective))
          )
        : CONVERSIONS.energy.MJ_TO_GJ(form.value.balance!.available_balance)
      : 0,
    0
  )

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
          {currentStep?.key === "recap" && (
            <Button
              priority="primary"
              onClick={() => mutation.execute()}
              loading={mutation.loading}
            >
              {t("Valider la teneur")}
            </Button>
          )}
        </>
      }
      fullWidth
    >
      <Main>
        <Stepper />
        {currentStep?.key !== biofuelFormStepKey && (
          <>
            {targetType && objective.target && (
              <Box gap="xs">
                <Text>{t("Rappel de votre progression")}</Text>

                <ProgressBar
                  baseQuantity={formatNumber(
                    CONVERSIONS.energy.MJ_TO_GJ(objective.teneur_declared),
                    0
                  )}
                  targetQuantity={formatNumber(
                    CONVERSIONS.energy.MJ_TO_GJ(objective.target),
                    0
                  )}
                  declaredQuantity={formatNumber(
                    CONVERSIONS.energy.MJ_TO_GJ(
                      objective.teneur_declared_month
                    ) + (form.value.quantity ?? 0),
                    0
                  )}
                />

                {targetType === TargetType.CAP && objective.target ? (
                  <RecapData.RemainingQuantityBeforeLimit
                    value={remainingEnergyBeforeLimitOrObjective}
                    bold
                    size="md"
                  />
                ) : null}
                {targetType === TargetType.REACH && objective.target ? (
                  <RecapData.RemainingQuantityBeforeObjective
                    value={remainingEnergyBeforeLimitOrObjective}
                    bold
                    size="md"
                  />
                ) : null}
              </Box>
            )}

            <Box>
              <RecapOperationGrid>
                <RecapOperation
                  balance={{
                    ...form.value.balance!,
                    available_balance: CONVERSIONS.energy.MJ_TO_GJ(
                      form.value.balance!.available_balance
                    ),
                  }}
                  unit={ExtendedUnit.GJ}
                />
                {currentStepIndex > 2 && (
                  <QuantitySummary values={form.value} unit={ExtendedUnit.GJ} />
                )}
              </RecapOperationGrid>
            </Box>
          </>
        )}
        {currentStep?.key !== "recap" && (
          <Box>
            <Form form={form}>
              {currentStep?.key === biofuelFormStepKey && (
                <BiofuelForm category={objective.code} />
              )}
              {currentStep?.key === quantityFormStepKey && (
                <QuantityForm
                  balance={form.value.balance!}
                  type={CreateOperationType.TENEUR}
                  depot_quantity_max={depotQuantityMax}
                  unit={ExtendedUnit.GJ}
                  backendUnit={Unit.MJ}
                  converter={CONVERSIONS.energy.GJ_TO_MJ}
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
