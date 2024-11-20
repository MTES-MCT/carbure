import type { Meta, StoryObj } from "@storybook/react"
import { Select } from "./select"
import { ReactNode, useState } from "react"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof Select<{ label: ReactNode; value: string }, string>> = {
  component: Select,
  title: "common/components/Select",
  args: {
    options: [
      { label: "Item 1", value: "1" },
      { label: "Item 2", value: "2" },
      { label: "Item 3", value: "3" },
    ],
  },
  render: (args) => {
    const [value, setValue] = useState<string | undefined>(args.value)

    return (
      <div style={{ width: "300px" }}>
        <Select {...args} value={value} onChange={(item) => setValue(item)} />
      </div>
    )
  },
}

type Story = StoryObj<
  typeof Select<{ label: ReactNode; value: string }, string>
>

export default meta

export const DefaultList: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const select = await waitFor(() => getByRole("button"))
    await userEvent.click(select)
  },
}

export const Search: Story = {
  ...DefaultList,
  args: {
    search: true,
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
  },
}

export const FullWidth: Story = {
  args: {
    full: true,
  },
}

export const CustomRenderer: Story = {
  args: {
    value: "1",
    valueRenderer: (item) => <div style={{ color: "red" }}>{item.label}</div>,
  },
}

export const LoadingState: Story = {
  args: {
    loading: true,
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
