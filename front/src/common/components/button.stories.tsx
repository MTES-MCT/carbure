import type { Meta, StoryObj } from "@storybook/react"

import { Button } from "./button"
import { Cross } from "./icons"

const meta: Meta<typeof Button> = {
  component: Button,
  args: {
    variant: "primary",
    label: "Button",
  },
  title: "ui/button",
}
type Story = StoryObj<typeof Button>

export default meta

export const AllVariants: Story = {
  args: {
    label: "Button",
  },
  render: (args) => {
    return (
      <div
        style={{
          display: "flex",
          gap: "8px",
          width: "fit-content",
          flexWrap: "wrap",
        }}
      >
        <Button {...args} label="Primary" />
        <Button {...args} variant="secondary" label="Secondary" />
        <Button {...args} variant="danger" label="Danger" />
        <Button {...args} variant="success" label="Success" />
        <Button {...args} variant="text" label="Simple text" />
        <Button {...args} variant="warning" label="Warning" />
        <Button {...args} variant="link" label="With link" />
        <Button {...args} variant="icon" icon={Cross} />
      </div>
    )
  },
}
