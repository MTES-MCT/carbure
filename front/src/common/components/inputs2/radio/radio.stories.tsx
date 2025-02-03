import type { Meta, StoryObj } from "@storybook/react"
import { RadioGroup } from "./radio"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { useState } from "react"
const meta: Meta<typeof RadioGroup> = {
  component: RadioGroup,
  title: "common/components/RadioGroup",
  args: {
    options: [
      {
        label: "Option 1",
        value: "1",
      },
      {
        label: "Option 2",
        value: "2",
      },
    ],
    onChange: fn(),
  },
}

type Story = StoryObj<typeof RadioGroup>

export default meta

export const Uncontrolled: Story = {
  play: async ({ canvasElement, args }) => {
    const { getByRole } = within(canvasElement)
    const radio = await waitFor(() => getByRole("radio", { name: "Option 2" }))

    await userEvent.click(radio)

    expect(args.onChange).toHaveBeenCalledWith("2")
  },
}

export const Controlled: Story = {
  render: (args) => {
    const [value, setValue] = useState(args.value)

    return <RadioGroup {...args} value={value} onChange={setValue} />
  },
  args: {
    value: "2",
  },
}
