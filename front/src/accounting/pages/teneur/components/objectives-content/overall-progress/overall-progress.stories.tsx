import type { Meta, StoryObj } from "@storybook/react"
import { OverallProgress } from "./overall-progress"
import { overallObjective } from "../../../__test__/data"
import { MockAnnualDeclarationTiruertProvider } from "accounting/providers/annual-declaration-tiruert.stories.utils"

const meta: Meta<typeof OverallProgress> = {
  title:
    "modules/accounting/pages/teneur/components/objectives-content/OverallProgress",
  component: OverallProgress,
  decorators: [
    (Story) => (
      <MockAnnualDeclarationTiruertProvider>
        <Story />
      </MockAnnualDeclarationTiruertProvider>
    ),
  ],
}

export default meta

type Story = StoryObj<typeof OverallProgress>

export const Default: Story = {
  args: {
    objective: overallObjective,
  },
  parameters: {
    mockingDate: new Date(2025, 11, 1),
  },
}

export const PreviousYearDeclaration: Story = {
  args: {
    objective: overallObjective,
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
