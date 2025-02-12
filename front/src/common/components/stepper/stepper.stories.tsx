import type { Meta, StoryObj } from "@storybook/react"
import { Stepper, useStepper } from "./stepper"
import { Button } from "../button2"

const meta: Meta<typeof Stepper> = {
  component: Stepper,
  title: "common/components/Stepper",
  parameters: {
    backgrounds: {
      default: "white",
      values: [{ name: "white", value: "white" }],
    },
  },
  render: () => {
    const {
      currentStep,
      currentStepIndex,
      steps,
      nextStep,
      hasPreviousStep,
      hasNextStep,
      goToNextStep,
      goToPreviousStep,
    } = useStepper([
      {
        key: "step-1",
        title: "Step 1",
      },
      {
        key: "step-2",
        title: "Step 2",
      },
      {
        key: "step-3",
        title: "Step 3",
      },
    ])

    return (
      <>
        <Stepper
          currentStep={currentStepIndex}
          stepCount={steps.length}
          title={currentStep?.title}
          nextTitle={nextStep?.title}
          marginBottom
        />
        <div>
          <Button disabled={!hasPreviousStep} onClick={goToPreviousStep}>
            Précédent
          </Button>
          <Button
            priority="secondary"
            disabled={!hasNextStep}
            onClick={goToNextStep}
          >
            Suivant
          </Button>
        </div>
      </>
    )
  },
}

type Story = StoryObj<typeof Stepper>

export default meta

export const Tertiary: Story = {}
