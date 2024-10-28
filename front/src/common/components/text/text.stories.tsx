import type { Meta, StoryObj } from "@storybook/react"

import { Text } from "./text"

const meta: Meta<typeof Text> = {
  component: Text,
}
type Story = StoryObj<typeof Text>

export default meta

export const OverrideHeadingStyle: Story = {
  args: {
    is: "h1",
    as: "h3",
    children: "This is a h1 with h3 visual style",
  },
}
