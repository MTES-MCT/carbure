import type { Meta, StoryObj } from "@storybook/react"
import { List } from "./list"
import { useState } from "react"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof List<{ label: string; value: string }, string>> = {
  component: List,
  args: {
    items: [
      { label: "Item 1", value: "1" },
      { label: "Item 2", value: "2" },
      { label: "Item 3", value: "3" },
    ],
  },
  render: (args) => {
    const [value, setValue] = useState<string | undefined>("")

    return (
      <List
        {...args}
        selectedValue={value}
        onSelectValue={(item) => setValue(item as string)}
      />
    )
  },
}

type Story = StoryObj<typeof List<{ label: string; value: string }, string>>

export default meta

export const DefaultList: Story = {}

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

export const SelectedValue: Story = {
  args: {
    ...DefaultList.args,
    selectedValue: "1",
  },
}

export const SelectedValues: Story = {
  args: {
    ...DefaultList.args,
    multiple: true,
    selectedValues: ["1", "2"],
  },
  render: (args) => {
    const [value, setValue] = useState<string[] | undefined>(
      args.selectedValues as string[]
    )

    return (
      <List
        {...args}
        selectedValues={value}
        onSelectValues={(items) => setValue(items as string[])}
      />
    )
  },
}

export const SearchList: Story = {
  args: {
    ...DefaultList.args,
    search: true,
  },
  play: async ({ canvasElement }) => {
    const input = await waitFor(() =>
      within(canvasElement).getByRole("searchbox")
    )
    await userEvent.type(input, "Item 3")
  },
}
