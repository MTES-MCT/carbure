import type { Meta, StoryObj } from "@storybook/react"
import { CheckboxGroup } from "./checkbox"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { useState } from "react"

const meta: Meta<typeof CheckboxGroup> = {
  component: CheckboxGroup,
  title: "common/components/CheckboxGroup",
  args: {
    onChange: fn(),
    onToggle: fn(),
    options: [
      {
        label: "Option 1",
        value: "option1",
      },
      {
        label: "Option 2",
        value: "option2",
      },
    ],
  },
}

type Story = StoryObj<typeof CheckboxGroup>

export default meta

export const Uncontrolled: Story = {}

export const Controlled: Story = {
  render: (args) => {
    const [value, setValue] = useState(args.value)

    return (
      <CheckboxGroup
        {...args}
        value={value}
        onChange={(values) => {
          setValue(values)
          args.onChange?.(values)
        }}
      />
    )
  },
  args: {
    value: ["option2"],
  },
  play: async ({ canvasElement, args }) => {
    const { getByText } = within(canvasElement)
    const checkbox1 = await waitFor(() => getByText("Option 1"))
    await userEvent.click(checkbox1)
    expect(args.onToggle).toHaveBeenCalledWith("option1", true)
    expect(args.onChange).toHaveBeenCalledWith(["option2", "option1"])
  },
}
