import type { Meta, StoryObj } from "@storybook/react"
import { Pagination } from "./pagination"
import { reactRouterParameters } from "storybook-addon-remix-react-router"

const meta: Meta<typeof Pagination> = {
  component: Pagination,
  title: "common/components/Pagination",
  parameters: {
    chromatic: { disableSnapshot: true },
  },
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
