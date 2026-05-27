import type { Meta, StoryObj } from "@storybook/react"
import { CategoryObjectiveProgressCard } from "./category-objective-progress-card"
import {
  cappedCategories,
  cappedCategoryWithLimitReached,
  objectivizedCategories,
} from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof CategoryObjectiveProgressCard> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/CategoryObjectiveProgressCard",
  component: CategoryObjectiveProgressCard,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <div style={{ width: "400px" }}>
          <Story />
        </div>
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
  args: {
    onCategoryClick: () => {},
    readOnly: false,
  },
}

export default meta

type Story = StoryObj<typeof CategoryObjectiveProgressCard>

export const Capped: Story = {
  args: {
    category: cappedCategories[0],
  },
}

export const Objectivized: Story = {
  args: {
    category: objectivizedCategories[0],
  },
}

export const CapReached: Story = {
  args: {
    category: cappedCategoryWithLimitReached,
  },
}

export const ReadOnly: Story = {
  args: {
    category: cappedCategories[0],
    readOnly: true,
  },
}

export const PreviousYearDeclaration: Story = {
  args: {
    category: cappedCategories[0],
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
        <div style={{ width: "400px" }}>
          <Story />
        </div>
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}
