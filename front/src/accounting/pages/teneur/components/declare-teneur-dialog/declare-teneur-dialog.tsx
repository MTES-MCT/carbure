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
import { RecapData } from "../recap-data"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import {
  CategoryObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../types"
import {
  ceilNumber,
  CONVERSIONS,
  floorNumber,
  formatUnit,
} from "common/utils/formatters"
import { computeObjectiveEnergy } from "../../utils/formatters"
import { useMemo } from "react"
import { Button } from "common/components/button2"
import { useDeclareTeneurDialog } from "./declare-teneur-dialog.hooks"
import { DeclareTeneurProgressBar } from "./declare-teneur-progress-bar"

interface DeclareTeneurDialogProps {
  onClose: () => void
  objective: CategoryObjective | UnconstrainedCategoryObjective
  // Only used for unconstrained categories
  sectorObjectives: SectorObjective[]
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
  sectorObjectives,
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
      objective.target ? computeObjectiveEnergy(objective) - quantity : 0
    )

    return formatUnit(remainingEnergy, ExtendedUnit.GJ, {
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
            form.value.balance!.available_balance,
            computeObjectiveEnergy(objective)
          )
        : form.value.balance!.available_balance
      : 0,
    0
  )
  // Get the current sector objective when the biofuel is selected
  const currentSectorObjective = useMemo(() => {
    if (!form.value.balance?.sector) return undefined

    return sectorObjectives.find(
      (sectorObjective) => sectorObjective.code === form.value.balance!.sector
    )
  }, [sectorObjectives, form.value.balance])

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
            <Box gap="xs">
              {targetType && objective.target && (
                <>
                  <DeclareTeneurProgressBar
                    teneurDeclared={objective.teneur_declared}
                    teneurDeclaredMonth={objective.teneur_declared_month}
                    target={objective.target}
                    quantity={form.value.quantity ?? 0}
                    targetType={targetType}
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
                </>
              )}
              {/* Setup progress bar related to the sector objective for unconstrained categories */}
              {!targetType && currentSectorObjective ? (
                <>
                  <DeclareTeneurProgressBar
                    teneurDeclared={
                      currentSectorObjective?.teneur_declared ?? 0
                    }
                    teneurDeclaredMonth={
                      currentSectorObjective?.teneur_declared_month ?? 0
                    }
                    target={currentSectorObjective?.target ?? 0}
                    quantity={form.value.quantity ?? 0}
                    sector={currentSectorObjective?.code}
                    targetType={targetType}
                  />
                  <RecapData.RemainingQuantityBeforeObjective
                    value={formatUnit(
                      Math.max(
                        0,
                        computeObjectiveEnergy(currentSectorObjective) -
                          (form.value.quantity ?? 0)
                      ),
                      ExtendedUnit.GJ,
                      {
                        fractionDigits: 0,
                      }
                    )}
                    bold
                    size="md"
                  />
                </>
              ) : null}
            </Box>

            <Box>
              <RecapOperationGrid>
                <RecapOperation
                  balance={form.value.balance!}
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
                  // Send to the backend the quantity declared / the part of renewable energy share of the biofuel (converted to MJ)
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
