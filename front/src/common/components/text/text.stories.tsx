import type { Meta, StoryObj } from "@storybook/react"

import { Text } from "./text"

const meta: Meta<typeof Text> = {
  component: Text,
  title: "common/components/Text",
}
type Story = StoryObj<typeof Text>

export default meta

export const DefaultText: Story = {
  args: {
    children: "This is a default text",
  },
}

export const AllVariants: Story = {
  render: () => (
    <>
      <Text size="xl">this is a xl text</Text>
      <Text size="lg">this is a lg text</Text>
      <Text size="md">this is a md text</Text>
      <Text size="sm">this is a sm text</Text>
      <Text size="xs">this is a xs text</Text>
    </>
  ),
}

export const WithMargin: Story = {
  args: {
    children: "This is a default text",
    margin: true,
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}
