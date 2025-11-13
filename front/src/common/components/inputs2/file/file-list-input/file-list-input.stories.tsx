import type { Meta, StoryObj } from "@storybook/react"
import { FileListInput } from "./file-list-input"
import { useState } from "react"

const meta: Meta<typeof FileListInput> = {
  component: FileListInput,
  title: "common/components/inputs/FileListInput",
  args: {
    label: "Importer les fichiers sur la plateforme",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  render: (args) => {
    const [files, setFiles] = useState<FileList>()
    return <FileListInput {...args} value={files} onChange={setFiles} />
  },
}

type Story = StoryObj<typeof FileListInput>

export default meta

export const Default: Story = {}
