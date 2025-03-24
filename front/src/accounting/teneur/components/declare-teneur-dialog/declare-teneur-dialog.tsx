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
import { CreateOperationType, OperationSector } from "accounting/types"
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
} from "accounting/teneur/types"
import { CONVERSIONS } from "common/utils/formatters"
import {
  computeObjectiveEnergy,
  formatEnergy,
} from "accounting/teneur/utils/formatters"
import { useMemo } from "react"

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
  // const currentStep = { key: "recap" }

  const remainingEnergyBeforeLimitOrObjective = useMemo(() => {
    // Add quantity declared only if the "declare quantity" button has been clicked
    const quantity =
      form.value.avoided_emissions_min && form.value.quantity
        ? form.value.quantity
        : 0

    let remainingEnergy = 0
    if (targetType === TargetType.CAP && objective.target) {
      remainingEnergy =
        computeObjectiveEnergy(objective) -
        (quantity ? CONVERSIONS.energy.GJ_TO_MJ(quantity) : 0)
    }
    if (targetType === TargetType.REACH && objective.target) {
      remainingEnergy =
        computeObjectiveEnergy(objective) -
        (quantity ? CONVERSIONS.energy.GJ_TO_MJ(quantity) : 0)
    }
    return formatEnergy(remainingEnergy, {
      unit: ExtendedUnit.GJ,
    })
  }, [
    form.value.quantity,
    form.value.avoided_emissions_min,
    objective,
    targetType,
  ])

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
              {targetType && objective.target && (
                <ProgressBar
                  baseQuantity={objective.teneur_declared}
                  targetQuantity={objective.target}
                  declaredQuantity={
                    objective.teneur_declared_month +
                    (form.value.quantity
                      ? CONVERSIONS.energy.GJ_TO_MJ(form.value.quantity)
                      : 0)
                  }
                />
              )}
              {targetType === TargetType.CAP && objective.target && (
                <RecapData.RemainingQuantityBeforeLimit
                  value={remainingEnergyBeforeLimitOrObjective}
                />
              )}
              {targetType === TargetType.REACH && objective.target && (
                <RecapData.RemainingQuantityBeforeObjective
                  value={remainingEnergyBeforeLimitOrObjective}
                />
              )}
            </Box>
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
              </RecapOperationGrid>
            </Box>
          </>
        )}
        {currentStep?.key !== "recap" && objective.target && (
          <Box>
            <Form form={form}>
              {currentStep?.key === biofuelFormStepKey && (
                <BiofuelForm category={objective.code} />
              )}
              {currentStep?.key === quantityFormStepKey && (
                <QuantityForm
                  balance={form.value.balance!}
                  type={CreateOperationType.TENEUR}
                  depot_quantity_max={Math.min(
                    form.value.balance!.available_balance,
                    computeObjectiveEnergy(objective)
                  )}
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
  const form = useForm<DeclareTeneurDialogForm>({
    // quantity: 1000,
    // avoided_emissions: 1.5,
    // balance: {
    //   sector: OperationSector.DIESEL,
    //   initial_balance: 0,
    //   available_balance: 1564082157,
    //   quantity: {
    //     credit: 1569197157,
    //     debit: 5115000,
    //   },
    //   pending_teneur: 0,
    //   declared_teneur: 0,
    //   pending_operations: 2,
    //   unit: "mj",
    //   customs_category: CategoryEnum.CONV,
    //   biofuel: {
    //     id: 16,
    //     code: "EMHV",
    //   },
    // },
  })
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
