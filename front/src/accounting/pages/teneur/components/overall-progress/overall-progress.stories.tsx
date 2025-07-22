import type { Meta, StoryObj } from "@storybook/react-vite"
import { OverallProgress } from "./overall-progress"
import { overallObjective } from "../../__test__/data"

const meta: Meta<typeof OverallProgress> = {
  title: "modules/accounting/pages/teneur/components/OverallProgress",
  component: OverallProgress,
}

export default meta

type Story = StoryObj<typeof OverallProgress>

export const Default: Story = {
  args: {
    objective: overallObjective,
  },
}
