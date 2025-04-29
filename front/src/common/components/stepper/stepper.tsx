import {
  Stepper as DsfrStepper,
  StepperProps as DsfrStepperProps,
} from "@codegouvfr/react-dsfr/Stepper"
import styles from "./stepper.module.css"
import cl from "clsx"
import { Button } from "../button2"
import { useStepper } from "./stepper.provider"
import { useTranslation } from "react-i18next"
import { useMutation } from "common/hooks/async"

type AdditionalStepperProps = {
  marginBottom?: boolean
}

type StepperProps = DsfrStepperProps & AdditionalStepperProps

/**
 * DSFR stepper with custom style
 */
export const BaseStepper = ({
  marginBottom = false,
  ...props
}: StepperProps) => {
  return (
    <DsfrStepper
      {...props}
      className={cl(!marginBottom && styles["stepper--no-margin-bottom"])}
    />
  )
}

const StepperNextButton = () => {
  const { goToNextStep, currentStep, nextStep } = useStepper()
  const { t } = useTranslation()
  const mutation = useMutation(async () => {
    if (currentStep?.onClick) {
      await currentStep.onClick()
    }
    goToNextStep()
  })
  if (!nextStep) return null

  return (
    <Button
      priority="secondary"
      onClick={mutation.execute}
      disabled={
        currentStep.allowNextStep !== undefined
          ? !currentStep.allowNextStep
          : false
      }
      iconId="ri-arrow-right-s-line"
      iconPosition="right"
      loading={mutation.loading}
    >
      {t("Suivant")}
    </Button>
  )
}

const StepperPreviousButton = () => {
  const { goToPreviousStep, previousStep } = useStepper()
  const { t } = useTranslation()

  if (!previousStep) return null

  return (
    <Button
      priority="secondary"
      onClick={goToPreviousStep}
      iconId="ri-arrow-left-s-line"
    >
      {t("Précédent")}
    </Button>
  )
}

/**
 * Stepper with provider (used to simplify the usage of the stepper)
 */
export const Stepper = (props: AdditionalStepperProps) => {
  const { currentStep, currentStepIndex, steps, nextStep } = useStepper()

  return (
    <BaseStepper
      title={currentStep?.title}
      stepCount={steps.length}
      currentStep={currentStepIndex}
      nextTitle={nextStep?.title}
      {...props}
    />
  )
}

Stepper.Next = StepperNextButton
Stepper.Previous = StepperPreviousButton
