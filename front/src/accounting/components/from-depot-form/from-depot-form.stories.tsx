import type { Meta, StoryObj } from "@storybook/react"

import { FromDepotForm } from "./from-depot-form"
import { Form, useForm } from "common/components/form2"
import { FromDepotFormProps } from "./from-depot-form.types"
import { okGetDeliverySites } from "common/__test__/api"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof FromDepotForm> = {
  component: FromDepotForm,
  title: "modules/accounting/components/FromDepotForm",
  parameters: {
    msw: {
      handlers: [okGetDeliverySites],
    },
  },
  render: () => {
    const form = useForm<FromDepotFormProps>({})

    return (
      <Form form={form}>
        <FromDepotForm />
      </Form>
    )
  },
}
type Story = StoryObj<typeof FromDepotForm>

export default meta

export const SelectDepot: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole, getByText } = within(canvasElement)

    // Open the autocomplete
    const input = await waitFor(() => getByRole("textbox"))
    await userEvent.click(input)

    // Type in the input
    await userEvent.type(input, "Test")

    // Wait for the option to appear and click on it
    const option = await waitFor(() => getByText("Test Delivery Site"))
    await userEvent.click(option)
  },
}
