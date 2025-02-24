import {
  Stepper as DsfrStepper,
  StepperProps as DsfrStepperProps,
} from "@codegouvfr/react-dsfr/Stepper"
import { useState } from "react"
import styles from "./stepper.module.css"
import cl from "clsx"

type StepperProps = DsfrStepperProps & {
  marginBottom?: boolean
}
export const Stepper = ({ marginBottom = false, ...props }: StepperProps) => {
  return (
    <DsfrStepper
      {...props}
      className={cl(!marginBottom && styles["stepper--no-margin-bottom"])}
    />
  )
}

type Step<Key extends string> = {
  key: Key
  title: StepperProps["title"]
}

export const useStepper = <Key extends string>(steps: Step<Key>[]) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)

  const currentStep = steps[currentStepIndex]
  const hasPreviousStep = currentStepIndex > 0
  const previousStep = hasPreviousStep ? steps[currentStepIndex - 1] : null
  const hasNextStep = steps.length > currentStepIndex + 1
  const nextStep = hasNextStep ? steps[currentStepIndex + 1] : null

  const setStep = (stepKey: Step<Key>["key"]) => {
    const stepIndex = steps.findIndex((step) => step.key === stepKey)
    if (stepIndex !== -1) {
      setCurrentStepIndex(stepIndex)
    }
  }

  const goToNextStep = () => {
    if (hasNextStep) {
      setCurrentStepIndex(currentStepIndex + 1)
    }
  }

  const goToPreviousStep = () => {
    if (hasPreviousStep) {
      setCurrentStepIndex(currentStepIndex - 1)
    }
  }

  return {
    currentStep,
    currentStepIndex: currentStepIndex + 1, // Index displayed in the stepper, starts at 1
    hasPreviousStep,
    previousStep,
    hasNextStep,
    nextStep,
    setStep,
    goToNextStep,
    goToPreviousStep,
    steps,
  }
}
