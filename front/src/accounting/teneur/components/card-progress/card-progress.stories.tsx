import type { Meta, StoryObj } from "@storybook/react"
import { CardProgress } from "./card-progress"

const meta: Meta<typeof CardProgress> = {
  component: CardProgress,
  title: "pages/teneur/components/CardProgress",
  args: {
    title: "Essence",
    description: "Objectif en tonnes de CO2 évitées : 14",
    quantityObjective: 200,
    quantityDeclared: 57,
    availableQuantity: 114,
    mainValue: 134,
    mainText: "GJ",
  },
}

type Story = StoryObj<typeof CardProgress>

export default meta

export const Default: Story = {}

export const AvailableQuantityZero = {
  args: {
    availableQuantity: 0,
  },
}

export const QuantityDeclaredAndAvailableZero = {
  args: {
    availableQuantity: 0,
    quantityDeclared: 0,
  },
}

export const QuantityDeclaredZero = {
  args: {
    quantityDeclared: 0,
  },
}
