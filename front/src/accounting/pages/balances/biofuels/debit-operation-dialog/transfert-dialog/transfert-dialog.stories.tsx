import { Meta, StoryObj } from "@storybook/react"

import { TransfertDialog } from "./transfert-dialog"
import { balance } from "accounting/__test__/data/balances"
import { okFindEligibleTiruertEntities } from "accounting/components/recipient-form/__test__/api"
import {
  getBalancesWithUpdatedAvailableBalance,
  fillGHGRangeForm,
} from "accounting/components/ghg-range-form/ghg-range-form.stories.utils"
import { userEvent, waitFor, within } from "@storybook/test"
import { getViewport } from "@storybook/mocks/utils"
import {
  baseHandlers as quantityBaseHandlers,
  fillQuantityForm,
  fillQuantityInput,
} from "accounting/components/quantity-form/quantity-form.stories.utils"
import { fillRecipientForm } from "accounting/components/recipient-form/recipient-form.stories.utils"

const clickNextStepButton = async (canvasElement: HTMLElement) => {
  const { getByRole } = within(canvasElement)
  const nextStepButton = await waitFor(() =>
    getByRole("button", { name: "Suivant" })
  )
  await userEvent.click(nextStepButton)
}

const baseHandlers = [
  okFindEligibleTiruertEntities,
  getBalancesWithUpdatedAvailableBalance,
]

const meta: Meta<typeof TransfertDialog> = {
  component: TransfertDialog,
  title:
    "modules/accounting/pages/balances/biofuels/debit-operation-dialog/TransfertDialog",
  parameters: {
    viewport: getViewport("fullModal", { width: "1200px", height: "1100px" }),
    msw: {
      handlers: [...baseHandlers, ...quantityBaseHandlers],
    },
  },
  args: {
    balance,
  },
}
type Story = StoryObj<typeof TransfertDialog>

export default meta

export const FirstStep: Story = {
  play: async (canvas) => {
    const { canvasElement, step } = canvas

    await step("Fill the recipient input", async () => {
      await fillRecipientForm(canvasElement)
    })

    await step("Fill the GHG range input", async () => {
      await fillGHGRangeForm(canvasElement)
    })
  },
}

export const SecondStep: Story = {
  play: async (canvas) => {
    const { canvasElement } = canvas

    // Fill the first step
    await FirstStep.play?.(canvas)
    // Click on the next step button
    await clickNextStepButton(canvasElement)

    // Fill the second step
    await fillQuantityForm(canvasElement)
  },
}

export const SecondStepNextStepButtonDisabled: Story = {
  ...SecondStep,
  parameters: {
    docs: {
      description:
        "Second step - Could not switch to the next step when the quantity is not submitted",
    },
    msw: {
      handlers: [...baseHandlers, ...quantityBaseHandlers],
    },
  },
  play: async (canvas) => {
    // Fill the first step
    await FirstStep.play?.(canvas)
    // Click on the next step button
    await clickNextStepButton(canvas.canvasElement)

    // Fill the quantity input
    await fillQuantityInput(canvas.canvasElement, "1000")

    // Click on the next step button
    await clickNextStepButton(canvas.canvasElement)
  },
}

export const RecapStep: Story = {
  ...SecondStep,
  play: async (canvas) => {
    await SecondStep.play?.(canvas)
    await clickNextStepButton(canvas.canvasElement)
  },
}
