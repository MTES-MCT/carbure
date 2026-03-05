import type { Meta, StoryObj } from "@storybook/react"
import { UnconstrainedCategoriesProgress } from "./unconstrained-categories-progress"
import { unconstrainedCategories } from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof UnconstrainedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/UnconstrainedCategoriesProgress",
  component: UnconstrainedCategoriesProgress,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof UnconstrainedCategoriesProgress>

export const Default: Story = {
  args: {
    categories: unconstrainedCategories,
    onCategoryClick: () => {},
    readOnly: false,
  },
}
