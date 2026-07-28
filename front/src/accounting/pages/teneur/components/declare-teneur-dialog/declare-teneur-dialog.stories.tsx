import { Meta, StoryObj } from "@storybook/react"
import { DeclareTeneurDialog } from "./declare-teneur-dialog"
import { getViewport } from "@storybook/mocks/utils"
import { expect, userEvent, waitFor, within } from "@storybook/test"
import {
  fillQuantityInput,
  fillQuantityForm,
  baseHandlers as quantityBaseHandlers,
} from "accounting/components/quantity-form/quantity-form.stories.utils"
import { getBalancesWithUpdatedAvailableBalance } from "accounting/components/ghg-range-form/ghg-range-form.stories.utils"
import {
  clickNextStepButton,
  fillBiofuelFiltersStep,
  selectBiofuel,
} from "./declare-teneur-dialog.stories.utils"
import { okGetBalancesWithZeroAvailableBalance } from "accounting/__test__/api/biofuels/balances"
import {
  defaultCategoryObjective,
  defaultMainObjective,
  defaultSectorObjectives,
  defaultTargetType,
} from "../../__test__/data"
import { TargetType } from "../../types"

const baseHandlers = [
  getBalancesWithUpdatedAvailableBalance,
  ...quantityBaseHandlers,
]

const meta: Meta<typeof DeclareTeneurDialog> = {
  component: DeclareTeneurDialog,
  title: "modules/accounting/pages/teneur/components/DeclareTeneurDialog",
  parameters: {
    viewport: getViewport("fullModal", { width: "1200px", height: "1100px" }),
    msw: {
      handlers: baseHandlers,
    },
  },
  args: {
    onClose: () => {},
    objective: defaultCategoryObjective,
    sectorObjectives: defaultSectorObjectives,
    targetType: defaultTargetType,
  },
}

type Story = StoryObj<typeof DeclareTeneurDialog>

export default meta

export const FirstStepNominal: Story = {
  play: async ({ canvasElement }) => {
    await fillBiofuelFiltersStep(canvasElement)

    const nextStepButton = await waitFor(() =>
      within(canvasElement).getByRole("button", { name: "Suivant" })
    )
    await expect(nextStepButton).toBeEnabled()
  },
}

export const FirstStepBalanceZeroDisablesNext: Story = {
  parameters: {
    msw: {
      handlers: [
        okGetBalancesWithZeroAvailableBalance,
        ...quantityBaseHandlers,
      ],
    },
  },
  play: async ({ canvasElement }) => {
    await selectBiofuel(canvasElement)

    await waitFor(() => {
      within(canvasElement).getByText(/0\s+litres/i)
    })

    const nextStepButton = await waitFor(() =>
      within(canvasElement).getByRole("button", { name: "Suivant" })
    )
    await expect(nextStepButton).toBeDisabled()
  },
}

export const SecondStepQuantityMaxCappedByObjective: Story = {
  play: async ({ canvasElement }) => {
    await fillBiofuelFiltersStep(canvasElement)
    await clickNextStepButton(canvasElement)

    await fillQuantityInput(canvasElement, "12797")
    const validateButton = await waitFor(() =>
      within(canvasElement).getByRole("button", { name: "Valider la quantité" })
    )
    await userEvent.click(validateButton)

    await waitFor(() => {
      within(canvasElement).getByText(
        /supérieure à la quantité maximale autorisée/i
      )
    })
  },
}

export const SecondStepWithMainObjectiveCO2: Story = {
  args: {
    mainObjective: defaultMainObjective,
    targetType: defaultTargetType,
  },
  play: async ({ canvasElement }) => {
    await fillBiofuelFiltersStep(canvasElement)
    await clickNextStepButton(canvasElement)
    await fillQuantityForm(canvasElement, { quantity: "100", tC02: "25" })

    await waitFor(() => {
      within(canvasElement).getByText("Objectif global")
    })
  },
}

export const SecondStepTargetTypeReachDisplaysObjectiveLabel: Story = {
  args: {
    targetType: TargetType.REACH,
  },
  play: async ({ canvasElement }) => {
    await fillBiofuelFiltersStep(canvasElement)
    await clickNextStepButton(canvasElement)

    await waitFor(() => {
      within(canvasElement).getByText(/jusqu'à l'objectif/i)
    })

    await expect(
      within(canvasElement).queryByText(/jusqu'au plafond/i)
    ).not.toBeInTheDocument()
  },
}
