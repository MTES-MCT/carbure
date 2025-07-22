import type { Meta, StoryObj } from "@storybook/react-vite"
import { FileInput } from "./file-input"
import { useState } from "react"

const meta: Meta<typeof FileInput> = {
  component: FileInput,
  title: "common/components/inputs/FileInput",
  args: {
    label: "Importer le fichier sur la plateforme",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  render: (args) => {
    const [file, setFile] = useState<File>()
    return <FileInput {...args} value={file} onChange={setFile} />
  },
}

type Story = StoryObj<typeof FileInput>

export default meta

export const Default: Story = {}
