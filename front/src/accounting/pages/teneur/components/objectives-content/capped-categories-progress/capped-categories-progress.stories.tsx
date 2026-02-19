import type { Meta, StoryObj } from "@storybook/react"
import { CappedCategoriesProgress } from "./capped-categories-progress"
import { cappedCategories } from "../../../__test__/data"

const meta: Meta<typeof CappedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/CappedCategoriesProgress",
  component: CappedCategoriesProgress,
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
