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

export const Default: Story = {
  parameters: {
    docs: {
      description:
        "Display the available balance when the component is mounted",
    },
  },
}

export const AvailableBalanceWhenRangeIsChanged: Story = {
  parameters: {
    docs: {
      description: "Get the new available balance when the range is changed",
    },
  },
  play: async ({ canvasElement }) => {
    // For an unknown reason, the test pass but the range is not visually updated in the screenshot
    // However, this range is also used in another story, and it works there, so it's not a problem with the range itself
    // The result of the screenshot is not correct
    await fillGHGRangeForm(canvasElement)
  },
}
