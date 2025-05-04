import Dialog from "common/components/dialog2/dialog"
import { useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { FormManager, useForm, Form } from "common/components/form2"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
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
  MainObjective,
  SectorObjective,
  TargetType,
  UnconstrainedCategoryObjective,
} from "../../types"
import {
  CONVERSIONS,
  floorNumber,
  formatUnit,
  formatNumber,
} from "common/utils/formatters"
import { computeObjectiveEnergy } from "../../utils/formatters"
import { useMemo, useEffect, useState } from "react"
import { Button } from "common/components/button2"
import { useDeclareTeneurDialog } from "./declare-teneur-dialog.hooks"
import {
  DeclareTeneurProgressBar,
  DeclareTeneurProgressBarList,
} from "./declare-teneur-progress-bar"
import { RecapGHGRange } from "accounting/components/recap-ghg-range/recap-ghg-range"

interface DeclareTeneurDialogProps {
  onClose: () => void
  objective: CategoryObjective | UnconstrainedCategoryObjective
  // Only used for unconstrained categories
  sectorObjectives: SectorObjective[]
  targetType?: TargetType
  mainObjective?: MainObjective
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
  mainObjective,
}: DeclareTeneurDialogContentProps) => {
  const { t } = useTranslation()
  const { currentStep, currentStepIndex } = useStepper()
  const mutation = useDeclareTeneurDialog({
    onClose,
    onOperationCreated: () => {},
    values: form.value,
  })

  const remainingEnergyBeforeLimitOrObjective = useMemo(() => {
    // Add quantity declared only if the "declare quantity" button has been clicked
    const quantity = form.value.quantity ?? 0

    const remainingEnergy = Math.max(
      0,
      objective.target ? computeObjectiveEnergy(objective) - quantity : 0
    )

    return formatUnit(remainingEnergy, ExtendedUnit.GJ, {
      fractionDigits: 0,
    })
  }, [form.value.quantity, objective])

  const remainingCO2EmissionsBeforeObjective = (
    mainObjective: MainObjective
  ) => {
    const avoidedEmissions = form.value.avoided_emissions ?? 0
    const remainingCO2 = Math.max(
      0,
      mainObjective.target -
        mainObjective.teneur_declared -
        mainObjective.teneur_declared_month -
        avoidedEmissions
    )
    return formatNumber(remainingCO2, {
      fractionDigits: 0,
      mode: "ceil",
    })
  }

  const [remainingCO2Objective, setRemainingCO2Objective] = useState("")

  useEffect(() => {
    if (mainObjective) {
      const updatedValue = remainingCO2EmissionsBeforeObjective(mainObjective)
      setRemainingCO2Objective(updatedValue)
    }
  }, [form.value.avoided_emissions, mainObjective])

  // Define the maximum quantity that can be declared for the teneur
  // If a target is defined, the maximum quantity is the minimum between the available balance and the objective
  // Otherwise, the maximum quantity is the available balance
  const depotQuantityMax = floorNumber(
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
            <Box spacing="md">
              <RecapOperationGrid>
                <RecapOperation
                  balance={form.value.balance!}
                  unit={ExtendedUnit.GJ}
                />
                <RecapGHGRange
                  min={form.value.gesBoundMin}
                  max={form.value.gesBoundMax}
                />
                {currentStepIndex > 2 && (
                  <QuantitySummary values={form.value} unit={ExtendedUnit.GJ} />
                )}
              </RecapOperationGrid>
            </Box>
            {currentStep?.key !== "recap" && (
              <Box gap="xs" spacing="md">
                <DeclareTeneurProgressBarList
                  sectorObjective={currentSectorObjective}
                  categoryObjective={objective}
                  quantity={form.value.quantity ?? 0}
                  targetType={targetType}
                />

                {targetType && objective.target && (
                  <>
                    {targetType === TargetType.CAP && objective.target ? (
                      <RecapData.RemainingQuantityBeforeLimit
                        value={remainingEnergyBeforeLimitOrObjective}
                        bold
                        size="md"
                        category={objective.code}
                      />
                    ) : null}
                    {targetType === TargetType.REACH && objective.target ? (
                      <RecapData.RemainingQuantityBeforeObjective
                        value={remainingEnergyBeforeLimitOrObjective}
                        bold
                        size="md"
                        category={objective.code}
                      />
                    ) : null}
                  </>
                )}
                {!targetType && currentSectorObjective ? (
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
                ) : null}
              </Box>
            )}
          </>
        )}
        {currentStep?.key !== "recap" && (
          <Form form={form}>
            {currentStep?.key === biofuelFormStepKey && (
              <Box spacing="md">
                <BiofuelForm category={objective.code} />
              </Box>
            )}
            {currentStep?.key === quantityFormStepKey && (
              <>
                <Box spacing="md">
                  <QuantityForm.Quantity
                    balance={form.value.balance!}
                    type={CreateOperationType.TENEUR}
                    depot_quantity_max={depotQuantityMax}
                    unit={ExtendedUnit.GJ}
                    backendUnit={Unit.MJ}
                    // Send to the backend the quantity declared / the part of renewable energy share of the biofuel (converted to MJ)
                    converter={CONVERSIONS.energy.GJ_TO_MJ}
                    gesBoundMin={form.value.gesBoundMin}
                    gesBoundMax={form.value.gesBoundMax}
                  />
                </Box>
                {form.value.avoided_emissions_min ? (
                  <Box spacing="md">
                    <QuantityForm.AvoidedEmissions />
                    {mainObjective && (
                      <DeclareTeneurProgressBar
                        teneurDeclared={mainObjective.teneur_declared}
                        teneurDeclaredMonth={
                          mainObjective.teneur_declared_month
                        }
                        target={mainObjective.target}
                        quantity={form.value.avoided_emissions ?? 0}
                        targetType={TargetType.REACH}
                        label={t("Objectif global")}
                      />
                    )}
                    {mainObjective && (
                      <RecapData.RemainingQuantityBegoreCO2Objective
                        value={remainingCO2Objective}
                        bold
                        size="md"
                      />
                    )}
                  </Box>
                ) : null}
              </>
            )}
          </Form>
        )}
      </Main>
    </Dialog>
  )
}

export const DeclareTeneurDialog = (props: DeclareTeneurDialogProps) => {
  const { t } = useTranslation()

  const form = useForm<DeclareTeneurDialogForm>({
    gesBoundMin: undefined,
    gesBoundMax: undefined,
  })

  const backendUnit = Unit.MJ

  const quantityFormStep = useQuantityFormStep({
    balance: form.value.balance,
    converter: CONVERSIONS.energy.GJ_TO_MJ,
    form,
    backendUnit,
  })

  const steps = [
    biofuelFormStep(form.value),
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <DeclareTeneurDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
