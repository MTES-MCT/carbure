import { Meta, StoryObj } from "@storybook/react"
import { GHGRangeForm } from "./ghg-range-form"
import { Form, useForm } from "common/components/form2"
import { balance } from "accounting/__test__/data/balances"
import {
  fillGHGRangeForm,
  getBalancesWithUpdatedAvailableBalance,
} from "./ghg-range-form.stories.utils"

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
    await fillGHGRangeForm(canvasElement)
  },
}
