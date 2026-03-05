import type { Meta, StoryObj } from "@storybook/react"
import { CappedCategoriesProgress } from "./capped-categories-progress"
import { cappedCategories } from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof CappedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/CappedCategoriesProgress",
  component: CappedCategoriesProgress,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof CappedCategoriesProgress>

export const Default: Story = {
  args: {
    categories: cappedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
}

export const PreviousYearDeclaration: Story = {
  args: {
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
