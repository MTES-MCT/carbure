import { Meta, StoryObj } from "@storybook/react"

import { TransfertDialog } from "./transfert-dialog"
import { balance } from "accounting/__test__/data/balances"

const meta: Meta<typeof TransfertDialog> = {
  component: TransfertDialog,
  title:
    "modules/accounting/pages/balances/biofuels/debit-operation-dialog/TransfertDialog",
  parameters: {
    msw: {
      handlers: [],
    },
  },
}
type Story = StoryObj<typeof TransfertDialog>

export default meta

export const Default: Story = {
  args: {
    balance,
  },
}
