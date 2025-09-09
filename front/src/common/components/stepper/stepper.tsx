import {
  Stepper as DsfrStepper,
  StepperProps as DsfrStepperProps,
} from "@codegouvfr/react-dsfr/Stepper"
import styles from "./stepper.module.css"
import cl from "clsx"
import { Button, ButtonProps } from "../button2"
import { useStepper } from "./stepper.provider"
import { useTranslation } from "react-i18next"
import { PropsWithChildren } from "react"
import { Form, FormProps } from "../form2"

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

type StepperNextButtonProps = Pick<
  ButtonProps,
  "disabled" | "loading" | "nativeButtonProps"
>

const StepperNextButton = ({ loading, ...props }: StepperNextButtonProps) => {
  const { nextStep, mutation } = useStepper()
  const { t } = useTranslation()

  if (!nextStep) return null

  return (
    <Button
      {...props}
      priority="secondary"
      iconId="ri-arrow-right-s-line"
      iconPosition="right"
      type="submit"
      loading={loading ?? mutation.loading}
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

type StepperFormProps<T> = Exclude<FormProps<T>, "id"> & {
  id: string
} & PropsWithChildren

const StepperForm = <T,>({ children, ...props }: StepperFormProps<T>) => {
  const { currentStep, goToNextStep, mutation: onSubmitMutation } = useStepper()

  const onSubmit = async () => {
    if (currentStep.onSubmit) {
      await onSubmitMutation.execute()
    }
    goToNextStep()
  }

  return (
    <Form onSubmit={onSubmit} {...props}>
      {children}
    </Form>
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
Stepper.Form = StepperForm
