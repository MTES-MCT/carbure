import type { Meta, StoryObj } from "@storybook/react"
import { fn } from "@storybook/test"
import { useState } from "react"
import { ToggleSwitch } from "./toggle-switch"

const meta: Meta<typeof ToggleSwitch> = {
  component: ToggleSwitch,
  title: "common/components/inputs/ToggleSwitch",
  args: {
    label: "Notifications",
    onChange: fn(),
    value: false,
  },
  render: (args) => {
    const [value, setValue] = useState(args.value ?? false)
    const { defaultChecked, ...controlledArgs } = args
    void defaultChecked

    return (
      <ToggleSwitch
        {...controlledArgs}
        value={value}
        onChange={(checked, event) => {
          setValue(checked)
          args.onChange?.(checked, event)
        }}
      />
    )
  },
}

type Story = StoryObj<typeof ToggleSwitch>

export default meta

export const Default: Story = {}

export const Checked: Story = {
  args: {
    value: true,
  },
}

export const WithHelperText: Story = {
  args: {
    helperText: "Enable notifications for important updates.",
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
  },
}
