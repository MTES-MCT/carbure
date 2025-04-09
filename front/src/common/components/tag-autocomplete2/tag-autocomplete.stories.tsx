import type { Meta, StoryObj } from "@storybook/react"
import { TagAutocomplete } from "./tag-autocomplete"

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
