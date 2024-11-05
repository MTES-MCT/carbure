import type { Meta, StoryObj } from "@storybook/react"

import { Title } from "./title"

const meta: Meta<typeof Title> = {
  component: Title,
  title: "common/components/Title",
}
type Story = StoryObj<typeof Title>

export default meta

export const AllHeadings: Story = {
  render: () => (
    <>
      <Title is="h1">title h1</Title>
      <Title is="h2">title h2</Title>
      <Title is="h3">title h3</Title>
      <Title is="h4">title h4</Title>
      <Title is="h5">title h5</Title>
      <Title is="h6">title h6</Title>
    </>
  ),
}

export const OverridesHeadingStyle: Story = {
  args: {
    is: "h1",
    as: "h3",
    children: "This is a h1 with h3 visual style",
  },
}

export const Display: Story = {
  args: {
    is: "p",
    size: "lg",
    children: "This is a p with lg display style",
  },
}

export const OverridesWithStyle: Story = {
  args: {
    is: "h1",
    style: { fontSize: "20px" },
    children: "This is a h1 with 20px",
  },
}

export const WithMargin: Story = {
  args: {
    is: "h1",
    children: "This is a default text",
    margin: true,
  },
}
