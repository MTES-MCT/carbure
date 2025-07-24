import type { Meta, StoryObj } from "@storybook/react"
import { FilterMultiSelect2 } from "./filter-multiselect2"

const meta: Meta<typeof FilterMultiSelect2> = {
  component: FilterMultiSelect2,
  title: "common/molecules/FilterMultiSelect2",
  tags: ["IN PROGRESS"],
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  args: {
    filterLabels: {
      filtre1: "Filtre 1",
      filtre2: "Filtre 2",
      filtre3: "Filtre 3",
      filtre4: "Filtre 4",
      filtre5: "Filtre 5",
      filtre6: "Filtre 6",
      filtre7: "Filtre 7",
      filtre8: "Filtre 8",
      filtre9: "Filtre 9",
      filtre10: "Filtre 10",
    },
  },
  render: (args) => {
    return (
      <div style={{ width: "700px", border: "1px solid red" }}>
        <FilterMultiSelect2 {...args} />
      </div>
    )
  },
}

type Story = StoryObj<typeof FilterMultiSelect2>

export default meta

export const Default: Story = {}
