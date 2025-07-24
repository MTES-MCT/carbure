import type { Meta, StoryObj } from "@storybook/react"
import { Checkbox } from "./checkbox"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { useState } from "react"

const meta: Meta<typeof Checkbox> = {
  component: Checkbox,
  title: "common/components/Checkbox",
  args: {
    onChange: fn(),
    label: "Label checkbox",
  },
}

type Story = StoryObj<typeof Checkbox>

export default meta

export const Uncontrolled: Story = {
  play: async ({ canvasElement, args }) => {
    const { getByRole } = within(canvasElement)
    const checkbox = await waitFor(() => getByRole("checkbox"))
    await userEvent.click(checkbox)
    expect(args.onChange).toHaveBeenCalledWith(true)
  },
}

export const Controlled: Story = {
  render: (args) => {
    const [value, setValue] = useState(args.value)

    return <Checkbox {...args} value={value} onChange={setValue} />
  },
  args: {
    value: true,
  },
}

export const WithoutLabel: Story = {
  args: {
    label: undefined,
    small: true,
  },
  render: (args) => {
    const [value, setValue] = useState(args.value)

    return <Checkbox {...args} value={value} onChange={setValue} />
  },
}
