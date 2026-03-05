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
}
