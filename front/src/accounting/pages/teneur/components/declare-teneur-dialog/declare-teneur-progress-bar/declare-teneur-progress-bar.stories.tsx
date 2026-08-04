import type { Meta, StoryObj } from "@storybook/react"
import { expect, within } from "@storybook/test"
import { DeclareTeneurProgressBarList } from "./declare-teneur-progress-bar"
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
    quantityMj: 0,
    targetType: TargetType.CAP,
  },
}

export const WithDeclaredQuantity: Story = {
  args: {
    categoryObjective: defaultCategoryObjective,
    sectorObjective: defaultSectorObjectives[0],
    quantityMj: 50_000,
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
    quantityMj: 10_000,
    targetType: TargetType.REACH,
  },
}

export const SectorOnly: Story = {
  args: {
    sectorObjective: defaultSectorObjectives[0],
    quantityMj: 20_000,
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
