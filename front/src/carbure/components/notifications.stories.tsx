import type { Meta, StoryObj } from "@storybook/react"
import Notifications from "./notifications"

const meta: Meta<typeof Notifications> = {
  component: Notifications,
  title: "carbure/components/Notifications",
  args: {},
}

type Story = StoryObj<typeof Notifications>

export default meta

export const Default: Story = {}
