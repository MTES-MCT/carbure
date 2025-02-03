import type { Meta, StoryObj } from "@storybook/react"
import { FileListInput } from "./file-list-input"

const meta: Meta<typeof FileListInput> = {
  component: FileListInput,
  title: "common/components/inputs/FileListInput",
  args: {
    label: "Importer les fichiers sur la plateforme",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof FileListInput>

export default meta

export const Default: Story = {}
