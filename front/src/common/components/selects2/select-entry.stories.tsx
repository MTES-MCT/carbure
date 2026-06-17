import type { Meta, StoryObj } from "@storybook/react"
import { ReactNode, useState } from "react"
import { Select } from "./select-entry"

type Option = { label: ReactNode; value: number }

const options: Option[] = [
  { label: "Item 1", value: 1 },
  { label: "Item 2", value: 2 },
  { label: "Item 3", value: 3 },
]

const meta: Meta<typeof Select<Option, number>> = {
  component: Select,
  title: "common/components/selects2/Select",
}

export default meta

type Story = StoryObj<typeof Select<Option, number>>

function SelectButtonStory() {
  const [value, setValue] = useState<number | undefined>()

  return (
    <div style={{ width: "300px" }}>
      <Select
        options={options}
        value={value}
        onChange={(item) => setValue(item)}
      />
    </div>
  )
}

function SelectFieldStory() {
  const [value, setValue] = useState<number | undefined>()

  return (
    <div style={{ width: "300px" }}>
      <Select
        variant="field"
        label="Label of the select"
        options={options}
        value={value}
        onChange={(item) => setValue(item)}
      />
    </div>
  )
}

function SelectFieldReadOnlyStory() {
  return (
    <div style={{ width: "300px" }}>
      <Select
        variant="field"
        label="Label of the select"
        options={options}
        value={2}
        readOnly
      />
    </div>
  )
}

function SelectFieldSuccessStateStory() {
  const [value, setValue] = useState<number | undefined>()

  return (
    <div style={{ width: "300px" }}>
      <Select
        variant="field"
        label="Label of the select"
        options={options}
        value={value}
        onChange={(item) => setValue(item)}
        state="success"
      />
    </div>
  )
}

export const Button: Story = {
  render: SelectButtonStory,
}

export const Field: Story = {
  render: SelectFieldStory,
}

export const FieldReadOnly: Story = {
  render: SelectFieldReadOnlyStory,
}

export const FieldSuccessState: Story = {
  render: SelectFieldSuccessStateStory,
}
