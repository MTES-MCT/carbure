import type { Meta, StoryObj } from "@storybook/react"
import { NumberInput } from "./number-input"
import { useState } from "react"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof NumberInput> = {
  component: NumberInput,
  title: "common/components/inputs/NumberInput",
  render: (args) => {
    const [value, setValue] = useState<number | undefined>(args.value)

    return (
      <NumberInput
        {...args}
        value={value}
        onChange={(value) => {
          setValue(value)
          args.onChange?.(value)
        }}
      />
    )
  },
  args: {
    label: "Label au dessus de linput",
    placeholder: "placeholder",
  },
}

type Story = StoryObj<typeof NumberInput>

export default meta

export const Default: Story = {
  play: async ({ canvasElement, args }) => {
    const { getByRole } = within(canvasElement)
    const input = await waitFor(() => getByRole("spinbutton"))

    await userEvent.type(input, "145")

    expect(args.onChange).toHaveBeenCalledWith(145)
  },
  args: {
    onChange: fn(),
  },
}

export const WithValue: Story = {
  args: {
    value: 1458,
  },
}

export const ReadOnly: Story = {
  args: {
    readOnly: true,
    value: 1458,
  },
}
