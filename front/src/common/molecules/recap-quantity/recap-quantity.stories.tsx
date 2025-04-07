import { Meta, StoryObj } from "@storybook/react"
import { expect, fn, userEvent, within } from "@storybook/test"
import { RecapQuantity } from "./recap-quantity"

const meta: Meta<typeof RecapQuantity> = {
  title: "common/molecules/RecapQuantity",
  component: RecapQuantity,
  args: {
    text: "Texte à afficher",
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

export default meta
type Story = StoryObj<typeof RecapQuantity>

export const Default: Story = {}

export const WithClickHandler: Story = {
  args: {
    onRecapClick: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement)
    const recapElement = canvas.getByRole("button")

    await userEvent.click(recapElement)

    await expect(args.onRecapClick).toHaveBeenCalled()
  },
}
