import Dialog from "common/components/dialog2/dialog"
import { useTranslation } from "react-i18next"
import { Stepper, StepperProvider, useStepper } from "common/components/stepper"
import { FormManager, useForm } from "common/components/form2"
import { DeclareTeneurDialogForm } from "./declare-teneur-dialog.types"
import {
  QuantityForm,
  quantityFormStepKey,
  QuantitySummary,
  useQuantityFormStep,
} from "accounting/components/quantity-form"
import { Box, Main } from "common/components/scaffold"
import {
  BiofuelFiltersForm,
  biofuelFiltersFormStep,
  biofuelFiltersFormStepKey,
} from "./biofuel-filters-form"
import { ExtendedUnit } from "common/types"
import { CreateOperationType } from "accounting/types"
import { RecapData } from "../recap-data"
import {
  RecapOperation,
  RecapOperationGrid,
} from "accounting/components/recap-operation"
import {
  BiofuelUnconstrainedCategoryObjective,
  CategoryObjective,
  MainObjective,
  SectorObjective,
  TargetType,
} from "../../types"
import { useMemo } from "react"
import { Button } from "common/components/button2"
import {
  useCalculateQuantityMax,
  useDeclareTeneurDialog,
  useRemainingCO2Objective,
} from "./declare-teneur-dialog.hooks"
import {
  DeclareTeneurProgressBar,
  DeclareTeneurProgressBarList,
} from "./declare-teneur-progress-bar"
import { useFocusOnAvoidedEmissions } from "accounting/components/quantity-form/quantity-form.hooks"
interface DeclareTeneurDialogProps {
  onClose: () => void
  objective: CategoryObjective | BiofuelUnconstrainedCategoryObjective
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
  const { avoidedEmissionsInputRef, handleQuantityDeclared } =
    useFocusOnAvoidedEmissions()

  const remainingCO2Objective = useRemainingCO2Objective(
    form.value,
    mainObjective
  )

  const depotQuantityMax = useCalculateQuantityMax(objective, form.value)
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
          <Stepper.Next nativeButtonProps={{ form: "declare-teneur-dialog" }} />
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
        {currentStep?.key !== biofuelFiltersFormStepKey && (
          <>
            <Box spacing="md">
              <RecapOperationGrid>
                <RecapOperation balance={form.value.balance!} />
                {currentStepIndex > 2 && (
                  <QuantitySummary values={form.value} unit={ExtendedUnit.GJ} />
                )}
              </RecapOperationGrid>
            </Box>
            {currentStep?.key !== "recap" && (
              <Box spacing="md">
                <DeclareTeneurProgressBarList
                  sectorObjective={currentSectorObjective}
                  categoryObjective={objective}
                  quantity={form.value.quantity ?? 0}
                  targetType={targetType}
                />
              </Box>
            )}
          </>
        )}
        {currentStep?.key !== "recap" && (
          <Stepper.Form form={form} id="declare-teneur-dialog">
            {currentStep?.key === biofuelFiltersFormStepKey && (
              <BiofuelFiltersForm category={objective.code} />
            )}
            {currentStep?.key === quantityFormStepKey && (
              <>
                <Box spacing="md">
                  <QuantityForm.Quantity
                    balance={form.value.balance!}
                    type={CreateOperationType.TENEUR}
                    quantityMax={depotQuantityMax}
                    unit={ExtendedUnit.GJ}
                    onQuantityDeclared={handleQuantityDeclared}
                  />
                </Box>
                {form.value.avoided_emissions_min ? (
                  <Box spacing="md">
                    <QuantityForm.AvoidedEmissions
                      inputRef={avoidedEmissionsInputRef}
                    />
                    {mainObjective && (
                      <DeclareTeneurProgressBar
                        teneurDeclared={mainObjective.teneur_declared}
                        pendingTeneur={mainObjective.pending_teneur}
                        target={mainObjective.target}
                        quantity={form.value.avoided_emissions ?? 0}
                        label={t("Objectif global")}
                      />
                    )}
                    {remainingCO2Objective && (
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
          </Stepper.Form>
        )}
      </Main>
    </Dialog>
  )
}

export const DeclareTeneurDialog = (props: DeclareTeneurDialogProps) => {
  const { t } = useTranslation()

  const form = useForm<DeclareTeneurDialogForm>({})

  const quantityFormStep = useQuantityFormStep({
    balance: form.value.balance,
    unit: ExtendedUnit.GJ,
    form,
  })

  const steps = [
    biofuelFiltersFormStep(form.value),
    quantityFormStep,
    { key: "recap", title: t("Récapitulatif") },
  ]
  return (
    <StepperProvider steps={steps}>
      <DeclareTeneurDialogContent {...props} form={form} />
    </StepperProvider>
  )
}
