import { Meta, StoryObj } from "@storybook/react"
import { GHGRangeForm } from "./ghg-range-form"
import { Form, useForm } from "common/components/form2"
import { balance } from "accounting/__test__/data/balances"
import { getBalancesWithUpdatedAvailableBalance } from "./ghg-range-form.stories.utils"
import { expect, fireEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof GHGRangeForm> = {
  component: GHGRangeForm,
  title: "modules/accounting/components/GHGRangeForm",
  parameters: {
    msw: {
      handlers: [getBalancesWithUpdatedAvailableBalance],
    },
  },
  args: {
    balance,
  },
  render: (args) => {
    const form = useForm({})

    return (
      <Form form={form}>
        <GHGRangeForm {...args} />
      </Form>
    )
  },
}
type Story = StoryObj<typeof GHGRangeForm>

export default meta

// Display the available balance when the component is mounted
export const Default: Story = {}

// Get the new available balance when the range is changed
export const AvailableBalanceWhenRangeIsChanged: Story = {
  play: async ({ canvasElement }) => {
    const { getAllByRole, getByText } = within(canvasElement)
    const range = await waitFor(() => getAllByRole("slider"))
    const firstCursor = range[0]
    if (!firstCursor) throw new Error("First cursor not found")

    await waitFor(async () => {
      await fireEvent.change(firstCursor, { target: { value: "50" } })
      return expect(firstCursor).toHaveValue("50")
    })
    await new Promise((resolve) => setTimeout(resolve, 1000))
    await await waitFor(() => getByText("2 500 litres"))
  },
}
