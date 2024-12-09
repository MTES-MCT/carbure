import type { Meta, StoryObj } from "@storybook/react"
import { ShowMore } from "./show-more"

const meta: Meta<typeof ShowMore> = {
  component: ShowMore,
  title: "common/components/ShowMore",
  tags: ["IN PROGRESS"],
  render: (args) => {
    return (
      <div style={{ width: "300px" }}>
        <ShowMore {...args} />
      </div>
    )
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
}

type Story = StoryObj<typeof ShowMore>

export default meta

export const Default: Story = {
  args: {
    children: [
      <div>premiere div</div>,
      <div>2 div</div>,
      <div>3 div</div>,
      <div>4 div</div>,
      <div>5 div</div>,
      <div>6 div</div>,
    ],
  },
}
