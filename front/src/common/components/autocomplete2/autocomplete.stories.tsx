import type { Meta, StoryObj } from "@storybook/react"
import { Autocomplete } from "./autocomplete"
import { useState } from "react"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof Autocomplete> = {
  component: Autocomplete,
  title: "common/components/Autocomplete",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type T = {
  id: string
  label: string
}

type Story = StoryObj<typeof Autocomplete<T, string>>

export default meta

export const Default: Story = {
  args: {
    label: "Organisation",
    placeholder: "Rechercher une société...",
    getOptions: () =>
      new Promise((resolve) => {
        setTimeout(() => {
          resolve([
            {
              id: "1",
              label: "Société 1",
            },
            {
              id: "2",
              label: "Société 2",
            },
            {
              id: "3",
              label: "Société 3",
            },
          ])
        }, 3000)
      }),
    normalize: (item) => ({
      label: item.label,
      value: item.id,
    }),
    value: "3",
  },
  render: (args) => {
    const [value, setValue] = useState(args.value)
    return (
      <Autocomplete
        {...args}
        value={value}
        onChange={(value) => {
          setValue(value)
          args.onChange?.(value)
        }}
      />
    )
  },
}

export const WithDebounce: Story = {
  args: {
    ...Default.args,
    debounce: 500,
    getOptions: fn(),
    value: undefined,
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement)
    const input = await waitFor(() =>
      canvas.getByPlaceholderText(args.placeholder ?? "")
    )
    await userEvent.click(input)

    // getOptions is called when the input is focused
    expect(args.getOptions).toHaveBeenCalledOnce()

    await userEvent.type(input, "test")

    // Wait for the debounce delay
    await new Promise((resolve) => setTimeout(resolve, args.debounce))

    // Check that onChange has been called
    expect(args.getOptions).toHaveBeenCalledTimes(2)
    expect(args.getOptions).toHaveBeenNthCalledWith(2, "test")
  },
}
