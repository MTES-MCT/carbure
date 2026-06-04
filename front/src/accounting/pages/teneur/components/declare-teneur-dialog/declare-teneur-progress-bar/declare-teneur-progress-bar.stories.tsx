import type { Meta, StoryObj } from "@storybook/react"
import { expect, within } from "@storybook/test"
import {
  DeclareTeneurProgressBar,
  DeclareTeneurProgressBarList,
} from "./declare-teneur-progress-bar"
import {
  defaultCategoryObjective,
  defaultSectorObjectives,
} from "../../../__test__/data"
import { TargetType } from "../../../types"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof DeclareTeneurProgressBarList> = {
  title:
    "modules/accounting/pages/teneur/components/declare-teneur-dialog/DeclareTeneurProgressBarList",
  component: DeclareTeneurProgressBarList,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof DeclareTeneurProgressBarList>

export const CappedCategoryAndSector: Story = {
  args: {
    categoryObjective: defaultCategoryObjective,
    sectorObjective: defaultSectorObjectives[0],
    quantity: 0,
    targetType: TargetType.CAP,
  },
}

export const WithDeclaredQuantity: Story = {
  args: {
    categoryObjective: defaultCategoryObjective,
    sectorObjective: defaultSectorObjectives[0],
    quantity: 50,
    targetType: TargetType.CAP,
  },
}

export const ObjectivizedCategory: Story = {
  args: {
    categoryObjective: {
      ...defaultCategoryObjective,
      target_type: TargetType.REACH,
    },
    sectorObjective: defaultSectorObjectives[0],
    quantity: 10,
    targetType: TargetType.REACH,
  },
}

export const SectorOnly: Story = {
  args: {
    sectorObjective: defaultSectorObjectives[0],
    quantity: 20,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    await expect(
      canvas.getByText(/Quantité restante jusqu.*objectif/i)
    ).toBeInTheDocument()
    await expect(
      canvas.queryByText(/Quantité restante jusqu.*plafond/i)
    ).not.toBeInTheDocument()
  },
}

export const ProgressBarWithoutRemaining: StoryObj<
  typeof DeclareTeneurProgressBar
> = {
  render: (args) => <DeclareTeneurProgressBar {...args} />,
  args: {
    teneurDeclared: 20,
    pendingTeneur: 10,
    target: 150,
    quantity: 5,
    label: "Objectif global",
  },
}
