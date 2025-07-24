import type { Meta, StoryObj } from "@storybook/react"
import { TextArea } from "./textarea"
import { useState } from "react"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof TextArea> = {
  component: TextArea,
  title: "common/components/inputs/TextArea",
  render: (args) => {
    const [value, setValue] = useState<string | undefined>(args.value)

    return (
      <TextArea
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

type Story = StoryObj<typeof TextArea>

export default meta

export const Default: Story = {
  play: async ({ canvasElement, args }) => {
    const { getByRole } = within(canvasElement)
    const input = await waitFor(() => getByRole("textbox"))

    await userEvent.type(input, "test")

    expect(args.onChange).toHaveBeenCalledWith("test")
  },
  args: {
    onChange: fn(),
    maxLength: 2000,
  },
}

export const WithValue: Story = {
  args: {
    value: "une valeur par defaut",
  },
}
