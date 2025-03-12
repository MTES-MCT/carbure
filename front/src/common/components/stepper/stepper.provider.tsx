import {
  createContext,
  useContext,
  PropsWithChildren,
  ReactNode,
  useState,
} from "react"

export type Step<Key extends string> = {
  key: Key
  title: ReactNode
  allowNextStep?: boolean
}

type StepperContextType<Steps extends Step<string>[]> = {
  currentStep: Steps[number]
  currentStepIndex: number
  steps: Steps
  hasPreviousStep: boolean
  previousStep: Steps[number] | null
  hasNextStep: boolean
  nextStep: Steps[number] | null
  goToNextStep: () => void
  goToPreviousStep: () => void
}

const StepperContext = createContext<StepperContextType<any> | undefined>(
  undefined
)

export function StepperProvider<Steps extends Step<string>[]>({
  children,
  steps,
}: PropsWithChildren<{
  steps: Steps
}>) {
  const stepperValue = useStepperManager(steps)

  return (
    <StepperContext.Provider value={stepperValue}>
      {children}
    </StepperContext.Provider>
  )
}

export function useStepper<Steps extends Step<string>[]>() {
  const context = useContext(StepperContext)
  if (!context) {
    throw new Error("useStepperContext must be used within a StepperProvider")
  }
  return context as StepperContextType<Steps>
}

const useStepperManager = <Steps extends Step<string>[]>(steps: Steps) => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const currentStep = steps[currentStepIndex]

  const hasPreviousStep = currentStepIndex > 0
  const previousStep = hasPreviousStep ? steps[currentStepIndex - 1] : null
  const hasNextStep = steps.length > currentStepIndex + 1
  const nextStep = hasNextStep ? steps[currentStepIndex + 1] : null

  const setStep = (stepKey: Steps[number]["key"]) => {
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
