import type { Meta, StoryObj } from "@storybook/react"
import { ObjectivizedCategoriesProgress } from "./objectivized-categories-progress"
import { objectivizedCategories } from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof ObjectivizedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/ObjectivizedCategoriesProgress",
  component: ObjectivizedCategoriesProgress,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof ObjectivizedCategoriesProgress>

export const Default: Story = {
  args: {
    categories: objectivizedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
}
