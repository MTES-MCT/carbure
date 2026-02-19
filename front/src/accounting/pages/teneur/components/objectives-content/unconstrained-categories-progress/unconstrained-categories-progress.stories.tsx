import type { Meta, StoryObj } from "@storybook/react"
import { UnconstrainedCategoriesProgress } from "./unconstrained-categories-progress"
import { unconstrainedCategories } from "../../../__test__/data"

const meta: Meta<typeof UnconstrainedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/UnconstrainedCategoriesProgress",
  component: UnconstrainedCategoriesProgress,
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
