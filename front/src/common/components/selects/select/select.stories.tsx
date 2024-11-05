import type { Meta, StoryObj } from "@storybook/react"
import { Select } from "./select"
import { ReactNode, useState } from "react"

const meta: Meta<typeof Select<{ label: ReactNode; value: string }, string>> = {
  component: Select,
  args: {
    options: [
      { label: <div style={{ color: "red" }}>Item 1</div>, value: "1" },
      { label: "Item 2", value: "2" },
      { label: "Item 3", value: "3" },
    ],
  },
  render: (args) => {
    const [value, setValue] = useState<string | undefined>(args.value)

    return (
      <Select {...args} value={value} onChange={(item) => setValue(item)} />
    )
  },
}

type Story = StoryObj<
  typeof Select<{ label: ReactNode; value: string }, string>
>

export default meta

export const DefaultList: Story = {}

export const Search: Story = {
  args: {
    search: true,
  },
}

export const Loading: Story = {
  args: {
    loading: true,
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
  },
}
