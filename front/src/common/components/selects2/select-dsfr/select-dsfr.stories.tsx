import type { Meta, StoryObj } from "@storybook/react"
import { SelectDsfr } from "./select-dsfr"
import { ReactNode, useState } from "react"

const meta: Meta<
  typeof SelectDsfr<{ label: ReactNode; value: number }, number>
> = {
  component: SelectDsfr,
  title: "common/components/SelectDsfr",
  args: {
    options: [
      { label: "Item 1", value: 1 },
      { label: "Item 2", value: 2 },
      { label: "Item 3", value: 3 },
    ],
  },
  render: (args) => {
    const [value, setValue] = useState<number | undefined>(args.value)

    return (
      <div style={{ width: "300px" }}>
        <SelectDsfr
          {...args}
          value={value}
          onChange={(item) => {
            setValue(item)
            console.log(item)
          }}
        />
      </div>
    )
  },
}

type Story = StoryObj<
  typeof SelectDsfr<{ label: ReactNode; value: number }, string>
>

export default meta

export const Default: Story = {}
