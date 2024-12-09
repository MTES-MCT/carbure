import type { Meta, StoryObj } from "@storybook/react"
import { Button } from "./button"

const meta: Meta<typeof Button> = {
  component: Button,
  title: "common/components/Button",
  args: {
    children: "Button",
  },
}

type Story = StoryObj<typeof Button>

export default meta

export const Tertiary: Story = {
  args: {
    priority: "tertiary",
  },
}

export const LinkStyle: Story = {
  args: {
    customPriority: "link",
  },
}
