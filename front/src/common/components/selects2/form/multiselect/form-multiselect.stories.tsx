import type { Meta, StoryObj } from "@storybook/react"
import { FormMultiSelect } from "./form-multiselect"
import { ReactNode, useState } from "react"

const meta: Meta<
  typeof FormMultiSelect<{ label: ReactNode; value: number }, number>
> = {
  component: FormMultiSelect,
  title: "common/components/selects2/FormMultiSelect",
  args: {
    options: [
      { label: "Item 1", value: 1 },
      { label: "Item 2", value: 2 },
      { label: "Item 3", value: 3 },
      { label: "Item 4", value: 4 },
    ],
    label: "Label of the multiselect",
  },
  render: (args) => {
    const [value, setValue] = useState<number[] | undefined>(args.value)

    return (
      <div style={{ width: "300px" }}>
        <FormMultiSelect
          {...args}
          value={value}
          onChange={(items) => setValue(items)}
        />
      </div>
    )
  },
}

type Story = StoryObj<
  typeof FormMultiSelect<{ label: ReactNode; value: number }, number>
>

export default meta

export const Default: Story = {}

export const WithSelection: Story = {
  args: {
    value: [1, 2, 3],
  },
}

export const ReadOnly: Story = {
  args: {
    readOnly: true,
    value: [1, 2],
  },
}

export const SuccessState: Story = {
  args: {
    state: "success",
    value: [1, 2],
  },
}

export const Search: Story = {
  args: {
    search: true,
  },
}
