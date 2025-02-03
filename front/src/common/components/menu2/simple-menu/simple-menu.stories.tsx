import type { Meta, StoryObj } from "@storybook/react"
import { SimpleMenu } from "./simple-menu"

const meta: Meta<typeof SimpleMenu> = {
  component: SimpleMenu,
  title: "common/components/Menus/SimpleMenu",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof SimpleMenu>

export default meta

export const Default: Story = {
  args: {
    label: "Click me",
    children: <div>Content of the dropdown</div>,
  },
}
