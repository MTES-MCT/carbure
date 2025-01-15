import type { Meta, StoryObj } from "@storybook/react"
import { FileArea } from "./filearea"
import { DashboardLine } from "common/components/icon"

const meta: Meta<typeof FileArea> = {
  component: FileArea,
  title: "common/components/inputs/FileArea",
  render: (args) => {
    return (
      <FileArea {...args}>
        <div style={{ height: "400px" }}>Drag and drop content anywhere</div>
      </FileArea>
    )
  },
  args: {
    label: "Importer le fichier sur la plateforme",
    icon: DashboardLine,
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof FileArea>

export default meta

export const Default: Story = {}
