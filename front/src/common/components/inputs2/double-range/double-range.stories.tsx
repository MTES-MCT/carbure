import type { Meta, StoryObj } from "@storybook/react"
import { DoubleRange } from "./double-range"
import { useState } from "react"

const meta: Meta<typeof DoubleRange> = {
  component: DoubleRange,
  title: "common/components/inputs/DoubleRange",
  render: (args) => {
    const [minValue, setMinValue] = useState<number | undefined>(
      args.minRange?.value
    )
    const [maxValue, setMaxValue] = useState<number | undefined>(
      args.maxRange?.value
    )

    return (
      <DoubleRange
        {...args}
        minRange={{
          ...args.minRange,
          value: minValue,
          onChange: (value) => {
            setMinValue(value)
            args.minRange?.onChange?.(value)
          },
        }}
        maxRange={{
          ...args.maxRange,
          value: maxValue,
          onChange: (value) => {
            setMaxValue(value)
            args.maxRange?.onChange?.(value)
          },
        }}
      />
    )
  },
  args: {
    label: "Label au dessus du range",
  },
}

type Story = StoryObj<typeof DoubleRange>

export default meta

export const Default: Story = {
  args: {
    min: 0,
    max: 100,
  },
}

export const WithValue: Story = {
  args: {
    min: 0,
    max: 10,
    step: 0.1,
    minRange: {
      value: 2.0,
    },
    maxRange: {
      value: 8.0,
    },
  },
}
