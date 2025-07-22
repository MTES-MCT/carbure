import type { Meta, StoryObj } from "@storybook/react-vite"
import { CappedCategoriesProgress } from "./capped-categories-progress"
import { cappedCategories } from "../../__test__/data"

const meta: Meta<typeof CappedCategoriesProgress> = {
  title: "modules/accounting/pages/teneur/components/CappedCategoriesProgress",
  component: CappedCategoriesProgress,
}

export default meta

type Story = StoryObj<typeof CappedCategoriesProgress>

export const Default: Story = {
  args: {
    categories: cappedCategories,
  },
}
