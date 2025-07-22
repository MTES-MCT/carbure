import type { Meta, StoryObj } from "@storybook/react-vite"
import { Download } from "./download"

const meta: Meta<typeof Download> = {
  component: Download,
  title: "common/components/Download",
  args: {
    label: "Download",
    linkProps: {
      href: "#",
    },
  },
}

type Story = StoryObj<typeof Download>

export default meta

export const Default: Story = {}

export const WithDetails: Story = {
  args: {
    details: "Details",
  },
}
