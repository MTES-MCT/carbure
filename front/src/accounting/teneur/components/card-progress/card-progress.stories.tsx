import type { Meta, StoryObj } from "@storybook/react"
import { CardProgress } from "./card-progress"

const meta: Meta<typeof CardProgress> = {
  component: CardProgress,
  title: "pages/teneur/components/CardProgress",
  args: {
    title: "Essence",
    description: "Objectif en tonnes de CO2 évitées : 14",
    targetQuantity: 200,
    declaredQuantity: 57,
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
    declaredQuantity: 0,
  },
}

export const QuantityDeclaredZero = {
  args: {
    declaredQuantity: 0,
  },
}
