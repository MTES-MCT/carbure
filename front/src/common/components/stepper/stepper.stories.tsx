import type { Meta, StoryFn, StoryObj } from "@storybook/react-vite"
import { Stepper } from "./stepper"
import { Step, StepperProvider } from "./stepper.provider"
import { userEvent, waitFor, within } from "storybook/test"

const loadStepsDecorator = (steps: Step<string>[]) => (Story: StoryFn) => {
  return (
    <StepperProvider steps={steps}>
      <Story />
    </StepperProvider>
  )
}
const meta: Meta<typeof Stepper> = {
  component: Stepper,
  title: "common/components/Stepper",
  parameters: {
    backgrounds: {
      default: "white",
      values: [{ name: "white", value: "white" }],
    },
  },
  decorators: [
    loadStepsDecorator([
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
    ]),
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
  decorators: [
    loadStepsDecorator([
      {
        key: "step-1",
        title: "Step 1",
        allowNextStep: false,
      },
      {
        key: "step-2",
        title: "Step 2",
      },
    ]),
  ],
}

export const Step2: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const button = await waitFor(() => getByRole("button", { name: "Suivant" }))

    await userEvent.click(button)
  },
}
