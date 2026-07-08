import type { Meta, StoryObj } from "@storybook/react"
import { ReactNode, useState } from "react"
import { Select } from "./select"

const meta: Meta<typeof Select<{ label: ReactNode; value: number }, number>> = {
  component: Select,
  title: "common/components/selects2/Select",
  args: {
    options: [
      { label: "Item 1", value: 1 },
      { label: "Item 2", value: 2 },
      { label: "Item 3", value: 3 },
    ],
    label: "Label of the select",
  },
  render: (args) => {
    const [value, setValue] = useState<number | undefined>(args.value)

    return (
      <div style={{ width: "300px" }}>
        <Select {...args} value={value} onChange={(item) => setValue(item)} />
      </div>
    )
  },
}

type Story = StoryObj<
  typeof Select<{ label: ReactNode; value: number }, number>
>

export default meta

export const Filter: Story = {}

export const Form: Story = {
  args: {
    variant: "form",
  },
}

export const FormReadOnly: Story = {
  args: {
    variant: "form",
    readOnly: true,
    value: 2,
  },
}

export const FormSuccessState: Story = {
  args: {
    variant: "form",
    state: "success",
    value: 2,
  },
}
