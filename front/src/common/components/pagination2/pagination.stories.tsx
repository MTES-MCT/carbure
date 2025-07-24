import type { Meta, StoryObj } from "@storybook/react"
import { Pagination } from "./pagination"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import { expect, fn, userEvent, waitFor, within } from "@storybook/test"
import { useState } from "react"

const meta: Meta<typeof Pagination> = {
  component: Pagination,
  title: "common/components/Pagination",
}

type Story = StoryObj<typeof Pagination>

export default meta

export const Default: Story = {
  args: {
    defaultPage: 1,
    total: 100,
    limit: 10,
  },
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        searchParams: { test: "url" },
      },
    }),
  },
}

export const WithLimit: Story = {
  args: {
    total: 100,
    limit: 10,
    onLimit: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const { getByText } = within(canvasElement)
    const select = await waitFor(() => getByText("10 par page"))

    await userEvent.click(select)
    const option = await waitFor(() => getByText("25 par page"))
    await userEvent.click(option)

    expect(args.onLimit).toHaveBeenCalledWith(25)
  },
  render: (args) => {
    const [limit, setLimit] = useState(args.limit)

    return (
      <Pagination
        {...args}
        limit={limit}
        onLimit={(limit) => {
          setLimit(limit)
          args.onLimit(limit)
        }}
      />
    )
  },
}
