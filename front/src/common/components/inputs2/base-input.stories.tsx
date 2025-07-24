import type { Meta, StoryObj } from "@storybook/react"
import { BaseInput } from "./base-input"

const meta: Meta<typeof BaseInput> = {
  component: BaseInput,
  title: "common/components/inputs/BaseInput",
  args: {
    label: "Label au dessus de linput",
  },
}

type Story = StoryObj<typeof BaseInput>

export default meta

export const Default: Story = {}

export const Loading: Story = {
  args: {
    loading: true,
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

export const WithTooltip: Story = {
  args: {
    hasTooltip: true,
    required: true,
    label: "Hover to show tooltip",
    title: "Contenu d'une tooltip avec de la description",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
