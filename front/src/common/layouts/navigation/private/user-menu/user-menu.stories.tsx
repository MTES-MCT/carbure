import type { Meta, StoryObj } from "@storybook/react"
import { UserMenu } from "./user-menu"

const meta: Meta<typeof UserMenu> = {
  component: UserMenu,
  title: "layouts/navigation/private/UserMenu",
}

type Story = StoryObj<typeof UserMenu>

export default meta

export const Default: Story = {}
