import { Meta, StoryObj } from "@storybook/react"
import { GHGRangeForm } from "./ghg-range-form"
import { Form, useForm } from "common/components/form2"
import { balance } from "accounting/__test__/data/balances"
import { fireEvent, waitFor, within } from "@storybook/test"
import { http, HttpResponse } from "msw"
import { apiTypes } from "common/services/api-fetch.types"

const getBalancesWithUpdatedAvailableBalance = http.get(
  "/api/tiruert/operations/balance/",
  () => {
    return HttpResponse.json<apiTypes["PaginatedBalanceResponseList"]>({
      results: [
        {
          ...balance,
          available_balance: 2500,
        },
      ],
      count: 1,
    })
  }
)

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
    const { getAllByRole } = within(canvasElement)
    const range = await waitFor(() => getAllByRole("slider"))
    const firstCursor = range[0]
    if (!firstCursor) throw new Error("First cursor not found")

    fireEvent.change(firstCursor, { target: { value: "50" } })
  },
}
