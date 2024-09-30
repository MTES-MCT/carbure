import type { Meta, StoryObj } from "@storybook/react"

import { Button } from "./button"

const meta: Meta<typeof Button> = {
  component: Button,
  args: {
    variant: "primary",
    label: "Button",
  },
}
type Story = StoryObj<typeof Button>

export default meta

export const Primary: Story = {
  args: {
    label: "Button",
  },
}
