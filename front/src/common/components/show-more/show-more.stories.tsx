import type { Meta, StoryObj } from "@storybook/react"
import { ShowMore } from "./show-more"
import { Select } from "../selects2"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof ShowMore> = {
  component: ShowMore,
  title: "common/components/ShowMore",
  tags: ["IN PROGRESS"],
  render: (args) => {
    return (
      <div style={{ width: "700px", border: "1px solid red" }}>
        <ShowMore {...args}>
          <Select placeholder="Select1" />
          <Select placeholder="Select2" />
          <Select placeholder="Select3" />
          <Select placeholder="Select4" />
          <Select placeholder="Select5" />
          <Select placeholder="Select6" />
        </ShowMore>
      </div>
    )
  },
  parameters: {
    chromatic: { disableSnapshot: true },
  },
  args: {
    showMoreText: "Show more",
    showLessText: "Show less",
  },
}

type Story = StoryObj<typeof ShowMore>

export default meta

export const Default: Story = {
  // args: {
  //   children: (
  //     <>
  //       <Select placeholder="Select1" />
  //       <Select placeholder="Select2" />
  //       <Select placeholder="Select3" />
  //       <Select placeholder="Select4" />
  //       <Select placeholder="Select5" />
  //       <Select placeholder="Select6" />
  //       <Select placeholder="Select7" />
  //       <Select placeholder="Select8" />
  //       <Select placeholder="Select9" />
  //       <Select placeholder="Select10" />
  //     </>
  //   ),
  // },
}

export const WithAllItemsVisible: Story = {
  ...Default,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = await waitFor(() =>
      canvas.getByRole("button", { name: "Show more" })
    )
    await userEvent.click(button)
  },
}

export const WithoutOverflow: Story = {
  args: {
    children: [
      <Select placeholder="Select1" />,
      <Select placeholder="Select2" />,
    ],
  },
}
