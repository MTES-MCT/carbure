import type { Meta, StoryObj } from "@storybook/react"

import { QuantityForm } from "./quantity-form"
import { Form, useForm } from "common/components/form2"
import { CreateOperationType } from "accounting/types"
import { balance } from "accounting/__test__/data/balances"
import { userEvent, waitFor, within } from "@storybook/test"
import {
  okSimulateMinMaxWithEqualValues,
  okSimulateMinMaxWithZeroValues,
} from "accounting/__test__/api/biofuels/operations"
import { baseHandlers } from "./quantity-form.stories.utils"
import { getViewport } from "@storybook/mocks/utils"

const meta: Meta<typeof QuantityForm> = {
  component: QuantityForm,
  title: "modules/accounting/components/QuantityForm",
  args: {
    balance,
    type: CreateOperationType.TRANSFERT,
    quantityMax: 10000,
  },
  parameters: {
    msw: {
      handlers: baseHandlers,
    },
  },
  render: (args) => {
    const form = useForm({})

    return (
      <Form form={form}>
        <QuantityForm {...args} />
      </Form>
    )
  },
}
type Story = StoryObj<typeof QuantityForm>

export default meta

export const DefaultQuantityForm: Story = {}

// Set a value in the quantity input and the validate button should be enabled
export const ValidateQuantityButtonEnabled: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const input = await waitFor(() => getByRole("spinbutton"))

    await userEvent.type(input, "1000")
  },
}

// Display an error when the quantity is greater than the quantity max available
export const ShowErrorWhenQuantityIsGreaterThanQuantityMax: Story = {
  args: {
    quantityMax: 100,
  },
  play: async (props) => {
    await ValidateQuantityButtonEnabled.play?.(props)

    const { getByRole } = within(props.canvasElement)
    const button = await waitFor(() =>
      getByRole("button", { name: "Valider la quantité" })
    )

    await userEvent.click(button)
  },
}

// Show an error when the simulate min max returns zero values
export const ShowErrorWhenSimulateMinMaxReturnsZeroValues: Story = {
  parameters: {
    msw: {
      handlers: [okSimulateMinMaxWithZeroValues, ...baseHandlers],
    },
  },
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
}

// Display the avoided emissions component with the range returned by the backend when the quantity is declared
export const DisplayAvoidedEmissionsWhenQuantityIsDeclared: Story = {
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
}

// Focus on the avoided emissions input when the quantity is declared (visible when the viewport height is small)
export const FocusOnAvoidedEmissionsWhenQuantityIsDeclared: Story = {
  play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
  parameters: {
    viewport: getViewport("fullModal", { width: "1200px", height: "200px" }),
  },
}

// Display the avoided emissions component with the range returned by the backend when the quantity is declared with equal values
export const DisplayAvoidedEmissionsWhenQuantityIsDeclaredWithEqualValues: Story =
  {
    parameters: {
      msw: {
        // Overrides the simulate min max mock api by setting the needed mock as first
        handlers: [okSimulateMinMaxWithEqualValues, ...baseHandlers],
      },
    },
    play: ShowErrorWhenQuantityIsGreaterThanQuantityMax.play,
  }

// When the quantity is declared, the button should be replaced by a reset button that hides the avoided emissions component
export const ResetQuantityDeclared: Story = {
  play: async (props) => {
    const { getByRole } = within(props.canvasElement)
    await ShowErrorWhenQuantityIsGreaterThanQuantityMax.play?.(props)

    const button = await waitFor(() =>
      getByRole("button", { name: "Modifier" })
    )

    await userEvent.click(button)
  },
}
