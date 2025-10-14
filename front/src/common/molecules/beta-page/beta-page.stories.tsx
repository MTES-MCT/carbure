import type { Meta, StoryObj } from "@storybook/react"
import { BetaPage } from "./beta-page"

const meta: Meta<typeof BetaPage> = {
  title: "Molecules/BetaPage",
  component: BetaPage,
  parameters: {
    layout: "padded",
  },
  argTypes: {
    title: {
      control: "text",
      description: "Title to display before the badge",
    },
    text: {
      control: "text",
      description: "Custom text to display after the badge",
    },
  },
}

export default meta
type Story = StoryObj<typeof BetaPage>

export const Default: Story = {
  args: {},
}

export const WithTitle: Story = {
  args: {
    title: "Nouvelle fonctionnalité",
  },
}

export const WithCustomText: Story = {
  args: {
    text: "Cette fonctionnalité est en cours de développement et peut contenir des bugs.",
  },
}

export const WithTitleAndCustomText: Story = {
  args: {
    title: "Module comptabilité",
    text: "Cette fonctionnalité est en cours de développement et peut contenir des bugs.",
  },
}
