import type { Meta, StoryObj } from "@storybook/react"

import { TextInput } from "./input"
import { Cross } from "./icons"

const meta: Meta<typeof TextInput> = {
  component: TextInput,
  title: "ui/inputs",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
type Story = StoryObj<typeof TextInput>

export default meta

export const TextInputVariants: Story = {
  render: (args) => {
    return (
      <>
        <h1>Variants</h1>
        <div
          style={{
            display: "flex",
            gap: "8px",
            width: "fit-content",
            flexWrap: "wrap",
          }}
        >
          <TextInput {...args} variant="inline" value="Inline" />
          <TextInput {...args} variant="outline" value="Outline" />
          <TextInput {...args} variant="solid" value="Solid" />
          <TextInput {...args} variant="text" value="Text" />
        </div>
        <h1>States</h1>
        <div
          style={{
            display: "flex",
            gap: "8px",
            width: "fit-content",
            alignItems: "flex-end",
            flexWrap: "wrap",
          }}
        >
          <TextInput {...args} label="My label" value="with label" />
          <TextInput {...args} error="My error" value="with error" />
          {/* Not possible to screenshot loading */}
          {/* <TextInput {...args} loading value="loading state" /> */}
          <TextInput {...args} icon={Cross} value="with icon" />
          <TextInput
            {...args}
            value="with tooltip"
            hasTooltip
            title="content of tooltip"
            label="hover for tooltip"
          />
          <TextInput {...args} label="field required" required />
          <TextInput {...args} disabled value="disabled" />
          <TextInput
            {...args}
            rightContent={<span style={{ background: "red" }}>content</span>}
          />
        </div>
      </>
    )
  },
}

export const WithError: Story = {
  args: {
    error: "Error",
  },
}
