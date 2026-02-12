import css from "./custom-stepper.module.css"
import cl from "clsx"

type CustomStepperProps = {
  currentStep: number
  totalSteps: number
}
export const CustomStepper = ({
  currentStep,
  totalSteps,
}: CustomStepperProps) => {
  const numberSteps = Array.from(
    { length: totalSteps },
    (_, index) => index + 1
  )
  return (
    <div className={css["custom-stepper"]}>
      {numberSteps.map((step) => (
        <div
          key={step}
          className={cl(
            css["custom-stepper__step"],
            step === currentStep && css["custom-stepper__step--current"]
          )}
        />
      ))}
    </div>
  )
}
