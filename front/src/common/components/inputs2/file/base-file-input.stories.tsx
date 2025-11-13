import type { Meta, StoryObj } from "@storybook/react"
import { BaseFileInput } from "./base-file-input"

const meta: Meta<typeof BaseFileInput> = {
  component: BaseFileInput,
  title: "common/components/inputs/BaseFileInput",
  render: (args) => {
    return (
      <form>
        <BaseFileInput {...args} />
        <button type="submit">Submit</button>
      </form>
    )
  },
  args: {
    label: "Importer le fichier sur la plateforme",
  },
}

type Story = StoryObj<typeof BaseFileInput>

export default meta

export const Default: Story = {}

export const WithTooltip: Story = {
  args: {
    hasTooltip: true,
    required: true,
    label: "Hover to show tooltip",
    title: "Contenu d'une tooltip avec de la description",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
