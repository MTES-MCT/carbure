import type { Meta, StoryObj } from "@storybook/react"
import { SearchInput } from "./search-input"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof SearchInput> = {
  component: SearchInput,
  title: "common/components/inputs/search",
}

type Story = StoryObj<typeof SearchInput>

export default meta

export const Default: Story = {}

export const WithDebounce: Story = {
  args: {
    debounce: 1000,
    onChange: fn(),
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement)
    const input = await waitFor(() => canvas.getByRole("searchbox"))
    await userEvent.type(input, "test")

    // Check that onChange has NOT been called immediately
    expect(args.onChange).not.toHaveBeenCalled()

    // Wait for the debounce delay
    await new Promise((resolve) => setTimeout(resolve, args.debounce))

    // Check that onChange has been called after the delay
    await expect(args.onChange).toHaveBeenCalledWith("test")
    await expect(args.onChange).toHaveBeenCalledTimes(1)
  },
}
