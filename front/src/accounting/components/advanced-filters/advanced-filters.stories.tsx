import type { Meta, StoryObj } from "@storybook/react"
import { Form, useForm } from "common/components/form2"
import { AdvancedFiltersBalanceCard } from "./advanced-filters"
import { balance } from "accounting/__test__/data/balances"
import { userEvent, waitFor, within } from "@storybook/test"
import { fillGHGRangeForm } from "../ghg-range-form/ghg-range-form.stories.utils"
import {
  okGetBalances,
  okGetBalancesWithZeroAvailableBalance,
  okGetBalanceFiltersDurabilityPeriod,
  okGetBalancesWithUpdatedBoundsWhenDurabilityPeriodSelected,
} from "accounting/__test__/api/biofuels/balances"

const AdvancedFiltersStory = ({
  initialBalance = balance,
}: {
  initialBalance?: typeof balance
}) => {
  const form = useForm({})

  return (
    <Form form={form}>
      <AdvancedFiltersBalanceCard initialBalance={initialBalance} />
    </Form>
  )
}

const meta: Meta<typeof AdvancedFiltersBalanceCard> = {
  component: AdvancedFiltersBalanceCard,
  title: "modules/accounting/components/AdvancedFiltersBalanceCard",
  parameters: {
    msw: {
      handlers: [okGetBalances],
    },
  },
  render: () => <AdvancedFiltersStory />,
}

type Story = StoryObj<typeof AdvancedFiltersBalanceCard>

export default meta

export const NominalWithBalance: Story = {}

export const AvailableBalanceZeroWhenRangeChanges: Story = {
  parameters: {
    msw: {
      handlers: [okGetBalancesWithZeroAvailableBalance],
    },
  },
  play: async ({ canvasElement }) => {
    await fillGHGRangeForm(canvasElement)
    await waitFor(() => {
      within(canvasElement).getByText(/0\s+litre/i)
    })
  },
}

export const UpdateBoundsWhenFilterSelected: Story = {
  parameters: {
    msw: {
      handlers: [
        okGetBalanceFiltersDurabilityPeriod,
        okGetBalancesWithUpdatedBoundsWhenDurabilityPeriodSelected,
      ],
    },
  },
  play: async ({ canvasElement, step }) => {
    const { getByRole, getByText } = within(canvasElement)

    await step("Open durability filter", async () => {
      const durabilityFilterInput = await waitFor(() =>
        getByRole("button", { name: "Période de durabilité" })
      )
      await userEvent.click(durabilityFilterInput)
    })

    await step("Select durability period", async () => {
      const option = await waitFor(() => getByText("2024-01"))
      await userEvent.click(option)
    })

    // Click outside to close the dropdown
    canvasElement.click()

    await waitFor(() => {
      getByText("62.34%")
      getByText("78.91%")
    })
  },
}
