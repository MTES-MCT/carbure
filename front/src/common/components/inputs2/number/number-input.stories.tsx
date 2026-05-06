import type { Meta, StoryObj } from "@storybook/react"
import { NumberInput } from "./number-input"
import { useState } from "react"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

const NumberInputStory = (args: React.ComponentProps<typeof NumberInput>) => {
  const [value, setValue] = useState(args.value)

  return (
    <NumberInput
      {...args}
      value={value}
      onChange={(value) => {
        setValue(value)
        args.onChange?.(value)
      }}
      step={0.01}
    />
  )
}

const meta: Meta<typeof NumberInput> = {
  component: NumberInput,
  title: "common/components/inputs/NumberInput",
  render: (args) => <NumberInputStory {...args} />,
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

export const GroupThousandsOnChange: Story = {
  play: async ({ canvasElement, args }) => {
    const { getByRole } = within(canvasElement)
    const input = await waitFor(() => getByRole("textbox"))

    await userEvent.type(input, "12345")

    expect(args.onChange).toHaveBeenLastCalledWith(12345)

    await waitFor(() => {
      expect((input as HTMLInputElement).value).toMatch(/12.*345/)
    })
  },
  args: {
    onChange: fn(),
    groupThousands: true,
  },
}
