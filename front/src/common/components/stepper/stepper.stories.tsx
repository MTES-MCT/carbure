import type { Meta, StoryFn, StoryObj } from "@storybook/react"
import { Stepper } from "./stepper"
import { Step, StepperProvider, useStepper } from "./stepper.provider"
import { userEvent, waitFor, within } from "@storybook/test"
import { TextInput } from "../inputs2"
import { useForm } from "../form2"

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

export const StepperWithForm: Story = {
  parameters: {
    docs: {
      description:
        "Check an error validation message is displayed after submitting the form",
    },
  },
  render: () => {
    const { bind } = useForm<{
      field1?: string
    }>({
      field1: "",
    })
    const { currentStepIndex } = useStepper()
    return (
      <>
        <Stepper marginBottom />
        <Stepper.Form id="form-id">
          {currentStepIndex === 1 && <TextInput {...bind("field1")} required />}
        </Stepper.Form>
        <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
          <Stepper.Previous />
          <Stepper.Next nativeButtonProps={{ form: "form-id" }} />
        </div>
      </>
    )
  },
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const button = await waitFor(() => getByRole("button", { name: "Suivant" }))

    await userEvent.click(button)
  },
}

export const StepperWithFormValidate: Story = {
  ...StepperWithForm,
  parameters: {
    docs: {
      description: "Check if the form is validated after filling the input",
    },
  },

  play: async (props) => {
    const { getByRole } = within(props.canvasElement)
    const input = await waitFor(() => getByRole("textbox"))

    await userEvent.type(input, "test")
    await StepperWithForm.play?.(props)
  },
}

export const StepperWithNextButtonDisabled: Story = {
  ...StepperWithForm,
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
      {
        key: "step-3",
        title: "Step 3",
      },
    ]),
  ],
}
