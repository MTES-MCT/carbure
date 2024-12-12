import type { Meta, StoryObj } from "@storybook/react"
import { Pagination } from "./pagination"

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
    count: 100,
    getPageLinkProps: (page) => ({
      href: `/page/${page}`,
    }),
  },
}
