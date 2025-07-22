import type { Meta, StoryObj } from "@storybook/react-vite"
import { Tabs } from "./tabs"

const meta: Meta<typeof Tabs> = {
  component: Tabs,
  title: "common/components/Tabs",
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

export const Default: Story = {}

export const WithIcon: Story = {
  args: {
    tabs: [
      { key: "1", label: "Tab 1", icon: "ri-inbox-archive-fill" },
      { key: "2", label: "Tab 2", icon: "ri-inbox-archive-fill" },
    ],
  },
}

export const WithIconActive: Story = {
  args: {
    tabs: [
      {
        key: "1",
        label: "Tab 1",
        icon: "ri-inbox-archive-line",
        iconActive: "ri-inbox-archive-fill",
      },
      {
        key: "2",
        label: "Tab 2",
        icon: "ri-inbox-archive-line",
      },
    ],
  },
}

export const WithLinks: Story = {
  args: {
    tabs: [
      { key: "1", label: "Tab 1", path: "/tab1" },
      { key: "2", label: "Tab 2", path: "/tab2" },
    ],
  },
}
