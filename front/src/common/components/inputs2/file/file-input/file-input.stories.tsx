import type { Meta, StoryObj } from "@storybook/react"
import { FileInput } from "./file-input"

const meta: Meta<typeof FileInput> = {
  component: FileInput,
  title: "common/components/inputs/FileInput",
  args: {
    label: "Importer le fichier sur la plateforme",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof FileInput>

export default meta

export const Default: Story = {}
