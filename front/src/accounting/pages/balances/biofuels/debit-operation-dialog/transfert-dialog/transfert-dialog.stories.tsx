import { Meta, StoryObj } from "@storybook/react"

import { TransfertDialog } from "./transfert-dialog"
import { balance } from "accounting/__test__/data/balances"
import { okFindEligibleTiruertEntities } from "accounting/components/recipient-form/__test__/api"
import {
  getBalancesWithUpdatedAvailableBalance,
  fillGHGRangeForm,
  setGHGRangeValue,
} from "accounting/components/ghg-range-form/ghg-range-form.stories.utils"
import { expect, userEvent, waitFor, within } from "@storybook/test"
import { getViewport } from "@storybook/mocks/utils"
import {
  baseHandlers as quantityBaseHandlers,
  fillQuantityForm,
  fillQuantityInput,
} from "accounting/components/quantity-form/quantity-form.stories.utils"
import { fillRecipientForm } from "accounting/components/recipient-form/recipient-form.stories.utils"
import { okGetBalancesWithZeroAvailableBalance } from "accounting/__test__/api/biofuels/balances"

const getNextStepButton = async (canvasElement: HTMLElement) => {
  const { getByRole } = within(canvasElement)
  return waitFor(() => getByRole("button", { name: "Suivant" }))
}

const clickNextStepButton = async (canvasElement: HTMLElement) => {
  const nextStepButton = await getNextStepButton(canvasElement)
  await userEvent.click(nextStepButton)
}

const fillFirstStep = async (canvasElement: HTMLElement) => {
  await fillRecipientForm(canvasElement)
  await fillGHGRangeForm(canvasElement)
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
  play: async ({ canvasElement }) => {
    await fillFirstStep(canvasElement)
  },
}

export const SecondStep: Story = {
  play: async ({ canvasElement }) => {
    await fillFirstStep(canvasElement)
    await clickNextStepButton(canvasElement)

    await fillQuantityForm(canvasElement)
  },
}

export const FirstStepNextStepButtonDisabledWhenAvailableBalanceIsZero: Story =
  {
    parameters: {
      docs: {
        description:
          "First step - Disable next step when available balance is 0 after slider change.",
      },
      msw: {
        handlers: [
          okFindEligibleTiruertEntities,
          okGetBalancesWithZeroAvailableBalance,
          ...quantityBaseHandlers,
        ],
      },
    },
    play: async ({ canvasElement }) => {
      await fillRecipientForm(canvasElement)
      await setGHGRangeValue({
        canvasElement,
        cursorIndex: 0,
        value: "50",
      })

      await waitFor(() => {
        within(canvasElement).getByText(/0\s+litre/i)
      })

      const nextStepButton = await getNextStepButton(canvasElement)
      await expect(nextStepButton).toBeDisabled()
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
  play: async ({ canvasElement }) => {
    await fillFirstStep(canvasElement)
    await clickNextStepButton(canvasElement)

    await fillQuantityInput(canvasElement, "1000")

    await clickNextStepButton(canvasElement)
  },
}

export const RecapStep: Story = {
  ...SecondStep,
  play: async (canvas) => {
    await SecondStep.play?.(canvas)
    await clickNextStepButton(canvas.canvasElement)
  },
}
