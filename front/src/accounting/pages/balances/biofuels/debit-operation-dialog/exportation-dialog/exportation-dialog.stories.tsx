import { Meta, StoryObj } from "@storybook/react"

import { ExportationDialog } from "./exportation-dialog"
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
} from "accounting/components/quantity-form/quantity-form.stories.utils"
import { okGetDeliverySites } from "common/__test__/api"
import { fillFromDepotForm } from "accounting/components/from-depot-form/from-depot-form.stories.utils"
import {
  fillCountryForm,
  baseHandlers as countryBaseHandlers,
} from "./country-form/country-form.stories.utils"

const clickNextStepButton = async (canvasElement: HTMLElement) => {
  const { getByRole } = within(canvasElement)
  const nextStepButton = await waitFor(() =>
    getByRole("button", { name: "Suivant" })
  )
  await userEvent.click(nextStepButton)
}

const baseHandlers = [
  okGetDeliverySites,
  okFindEligibleTiruertEntities,
  getBalancesWithUpdatedAvailableBalance,
  ...countryBaseHandlers,
]

const meta: Meta<typeof ExportationDialog> = {
  component: ExportationDialog,
  title:
    "modules/accounting/pages/balances/biofuels/debit-operation-dialog/ExportationDialog",
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
type Story = StoryObj<typeof ExportationDialog>

export default meta

export const FirstStep: Story = {
  play: async (canvas) => {
    await fillFromDepotForm(canvas.canvasElement)
    await fillGHGRangeForm(canvas.canvasElement)
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

export const SecondStepNextDisabledWithTCO2OutsideRange: Story = {
  parameters: {
    docs: {
      description:
        "Second step - Could not switch to the next step when the tCO2 is outside the range",
    },
  },
  play: async (canvas) => {
    const { canvasElement } = canvas

    // Fill the first step
    await FirstStep.play?.(canvas)
    // Click on the next step button
    await clickNextStepButton(canvasElement)

    // Fill the second step and append a 00 to the tCO2 value to simulate a value outside the range
    await fillQuantityForm(canvasElement, { tC02: "10000" })
    // Click on the next step button
    await clickNextStepButton(canvasElement)
  },
}

export const ThirdStep: Story = {
  play: async (canvas) => {
    const { canvasElement } = canvas

    await SecondStep.play?.(canvas)
    await clickNextStepButton(canvasElement)
    await fillCountryForm(canvasElement)
  },
}

export const RecapStep: Story = {
  play: async (canvas) => {
    await ThirdStep.play?.(canvas)
    await clickNextStepButton(canvas.canvasElement)
  },
}
