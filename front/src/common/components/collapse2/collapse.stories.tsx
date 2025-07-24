import type { Meta, StoryObj } from "@storybook/react"
import { Collapse } from "./collapse"

const meta: Meta<typeof Collapse> = {
  component: Collapse,
  title: "common/components/Collapse",
  args: {
    children: "Collapse",
  },
}

type Story = StoryObj<typeof Collapse>

export default meta

export const Default: Story = {
  args: {
    label: "Collapse",
    icon: "ri-information-line",
    children: "content",
  },
}
