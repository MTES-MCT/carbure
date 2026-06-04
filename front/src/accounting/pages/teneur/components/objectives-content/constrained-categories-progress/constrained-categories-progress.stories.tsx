import type { Meta, StoryObj } from "@storybook/react"
import { ConstrainedCategoriesProgress } from "./constrained-categories-progress"
import {
  cappedCategories,
  objectivizedCategories,
} from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof ConstrainedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/ConstrainedCategoriesProgress",
  component: ConstrainedCategoriesProgress,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof ConstrainedCategoriesProgress>

export const Capped: Story = {
  args: {
    variant: "capped",
    categories: cappedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
}

export const Objectivized: Story = {
  args: {
    variant: "objectivized",
    categories: objectivizedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
}

export const PreviousYearDeclaration: Story = {
  args: {
    variant: "capped",
    categories: cappedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider
        value={{
          selectedYear: 2023,
          isDeclarationInCurrentPeriod: false,
          currentDeclarationYear: 2025,
        }}
      >
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}
