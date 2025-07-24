import type { Meta, StoryObj } from "@storybook/react"
import { CardProgress } from "./card-progress"
import Badge from "@codegouvfr/react-dsfr/Badge"

const meta: Meta<typeof CardProgress> = {
  component: CardProgress,
  title: "modules/accounting/pages/teneur/components/CardProgress",
  args: {
    title: "Essence",
    description: "Objectif en tonnes de CO2 évitées : 14",
    targetQuantity: 200,
    baseQuantity: 57,
    declaredQuantity: 114,
    mainValue: 134,
    mainText: "GJ",
    badge: (
      <CardProgress.DefaultBadge declaredQuantity={57} targetQuantity={200} />
    ),
    children: (
      <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
      </ul>
    ),
  },
  decorators: [
    (Story) => (
      <div style={{ width: "400px" }}>
        <Story />
      </div>
    ),
  ],
}

type Story = StoryObj<typeof CardProgress>

export default meta

export const Default: Story = {}

export const BaseQuantityZero = {
  args: {
    baseQuantity: 0,
  },
}

export const QuantityDeclaredAndBaseZero = {
  args: {
    baseQuantity: 0,
    declaredQuantity: 0,
  },
}

export const QuantityDeclaredZero = {
  args: {
    declaredQuantity: 0,
  },
}

export const CustomBadgeText = {
  args: {
    badge: <Badge severity="info">Custom badge text</Badge>,
  },
}

export const WithOnClick = {
  args: {
    onClick: () => alert("Clicked"),
  },
}
