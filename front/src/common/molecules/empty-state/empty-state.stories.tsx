import type { Meta, StoryObj } from "@storybook/react"
import { fn } from "@storybook/test"
import { EmptyState } from "./empty-state"

const meta: Meta<typeof EmptyState> = {
  title: "common/molecules/EmptyState",
  component: EmptyState,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta
type Story = StoryObj<typeof EmptyState>

export const Default: Story = {
  args: {
    title: "Vous n’avez pas encore saisi de stations d’hydrogène",
    description:
      "Veuillez saisir les informations de vos stations afin de pouvoir commencer à déclarer des lots d’hydrogène",
    buttonProps: {
      children: "Inscrire une station",
      iconId: "ri-add-line",
      onClick: fn(),
    },
  },
  decorators: [
    (Story) => (
      <div style={{ height: "100vh" }}>
        <Story />
      </div>
    ),
  ],
}
