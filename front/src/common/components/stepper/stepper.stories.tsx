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
  globals: {
    steps: [
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
      {
        key: "step-4",
        title: "Step 4",
      },
    ],
  },
  render: (_, context) => {
    const {
      currentStep,
      currentStepIndex,
      steps,
      nextStep,
      hasPreviousStep,
      hasNextStep,
      isNextStepAllowed,
      goToNextStep,
      goToPreviousStep,
    } = useStepper(context.globals.steps)

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
            disabled={!hasNextStep || !isNextStepAllowed}
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

export const Default: Story = {}

export const DisallowedNextStep: Story = {
  globals: {
    steps: [
      {
        key: "step-1",
        title: "Step 1",
        allowNextStep: () => false,
      },
      {
        key: "step-2",
        title: "Step 2",
      },
    ],
  },
}
