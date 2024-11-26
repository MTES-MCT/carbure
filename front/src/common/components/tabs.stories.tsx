import type { Meta, StoryObj } from "@storybook/react"
import { Tabs } from "./tabs"

const meta: Meta<typeof Tabs> = {
  component: Tabs,
  title: "legacy/Tabs",
  args: {
    tabs: [
      { key: "1", label: "Tab 1" },
      { key: "2", label: "Tab 2" },
    ],
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof Tabs>

export default meta

export const AllVariants: Story = {
  render: (args) => (
    <div
      style={{
        width: "100%",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
      }}
    >
      <Tabs {...args} />
      <Tabs {...args} variant="header" />
      <Tabs {...args} variant="main" />
      <Tabs {...args} variant="sticky" />
      <Tabs {...args} variant="switcher" />
    </div>
  ),
}
