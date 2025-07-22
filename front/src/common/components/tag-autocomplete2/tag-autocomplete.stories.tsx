import type { Meta, StoryObj } from "@storybook/react"
import { TagAutocomplete } from "./tag-autocomplete"
import { useState } from "react"

const meta: Meta<typeof TagAutocomplete> = {
  component: TagAutocomplete,
  title: "common/components/TagAutocomplete2",
  parameters: {
    chromatic: { disableSnapshot: true },
    backgrounds: {
      default: "white",
      values: [{ name: "white", value: "white" }],
    },
  },
  render: (args) => {
    const [value, setValue] = useState(args.value)
    return <TagAutocomplete {...args} value={value} onChange={setValue} />
  },
}

type Story = StoryObj<typeof TagAutocomplete>

export default meta

export const Default: Story = {
  args: {
    label: "Tags",
    placeholder: "Rechercher des tags...",
    options: ["tag1", "tag2", "tag3", "tag4", "tag5"],
    value: [],
  },
}

export const ReadOnly: Story = {
  args: {
    ...Default.args,
    readOnly: true,
    value: ["tag1", "tag2"],
  },
}

export const WithDefaultValues: Story = {
  args: {
    ...Default.args,
    value: ["tag1", "tag2"],
  },
}
