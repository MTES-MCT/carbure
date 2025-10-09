import type { Meta, StoryObj } from "@storybook/react"

import { QuantityForm } from "./quantity-form"
import { Form, useForm } from "common/components/form2"
import { okGetDeliverySites } from "common/__test__/api"
import { CreateOperationType } from "accounting/types"
import { balance } from "accounting/__test__/data"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof QuantityForm> = {
  component: QuantityForm,
  title: "modules/accounting/components/QuantityForm",
  args: {
    balance,
    type: CreateOperationType.TRANSFERT,
  },
  parameters: {
    msw: {
      handlers: [okGetDeliverySites],
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
    depot_quantity_max: 100,
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
