import type { Meta, StoryObj } from "@storybook/react"
import { List } from "./list"

const meta: Meta<typeof List> = {
  component: List,
}

type Story = StoryObj<typeof List>

export default meta

export const DefaultList: Story = {
  args: {
    items: [
      { label: "Item 1", value: "1" },
      { label: "Item 2", value: "2" },
      { label: "Item 3", value: "3" },
    ],
  },
}

export const CustomStyleList: Story = {
  args: {
    ...DefaultList.args,
    children: (item) => (
      <div style={{ background: "red" }}>
        List of div paragraphs : {item.label}
      </div>
    ),
  },
}
