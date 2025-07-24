import type { Meta, StoryObj } from "@storybook/react"
import { ObjectivizedCategoriesProgress } from "./objectivized-categories-progress"
import { objectivizedCategories } from "../../__test__/data"

const meta: Meta<typeof ObjectivizedCategoriesProgress> = {
  title:
    "modules/accounting/pages/teneur/components/ObjectivizedCategoriesProgress",
  component: ObjectivizedCategoriesProgress,
}

export default meta

type Story = StoryObj<typeof ObjectivizedCategoriesProgress>

export const Default: Story = {
  args: {
    categories: objectivizedCategories,
  },
}
