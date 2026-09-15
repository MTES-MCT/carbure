import type { Meta, StoryObj } from "@storybook/react"

import { YesNoIndicator } from "./yes-no-indicator"

const meta: Meta<typeof YesNoIndicator> = {
  component: YesNoIndicator,
  title: "common/components/YesNoIndicator",
}

type Story = StoryObj<typeof YesNoIndicator>

export default meta

export const Yes: Story = {
  args: {
    value: true,
  },
}

export const No: Story = {
  args: {
    value: false,
  },
}
