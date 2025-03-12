import type { Meta, StoryObj } from "@storybook/react"
import { Stepper } from "./stepper"
import { StepperProvider } from "./stepper.provider"
import { userEvent, waitFor, within } from "@storybook/test"

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
  decorators: [
    (Story, context) => {
      return (
        <StepperProvider steps={context.globals.steps}>
          <Story />
        </StepperProvider>
      )
    },
  ],
  render: () => {
    return (
      <>
        <Stepper marginBottom />
        <div style={{ display: "flex", gap: "8px" }}>
          <Stepper.Previous />
          <Stepper.Next />
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
        allowNextStep: false,
      },
      {
        key: "step-2",
        title: "Step 2",
      },
    ],
  },
  decorators: [
    (Story, context) => {
      return (
        <StepperProvider steps={context.globals.steps}>
          <Story />
        </StepperProvider>
      )
    },
  ],
}

export const Step2: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const button = await waitFor(() => getByRole("button", { name: "Suivant" }))

    await userEvent.click(button)
  },
}
