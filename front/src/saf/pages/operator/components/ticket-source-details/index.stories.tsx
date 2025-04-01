import type { Meta, StoryObj } from "@storybook/react"
import { TicketSourceDetails } from "./index"
import { okSafTicketSourceDetails } from "saf/__test__/api"
import { COMMON_MOCKS } from "@storybook/mocks/common"
import { reactRouterParameters } from "storybook-addon-remix-react-router"

const meta = {
  title: "SAF/Operator/TicketSourceDetails",
  component: TicketSourceDetails,
  parameters: {
    layout: "centered",
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { id: "123" },
        hash: "#ticket-source/123",
      },
      routing: {
        path: "/ticket-source/:id",
      },
    }),
    msw: {
      handlers: [...COMMON_MOCKS, okSafTicketSourceDetails],
    },
  },
} satisfies Meta<typeof TicketSourceDetails>

export default meta
type Story = StoryObj<typeof TicketSourceDetails>

// Mock data pour les props de navigation
const mockNavigationProps = {
  limit: 10,
  total: 100,
  baseIdsList: [],
  fetchIdsForPage: async () => [],
}

export const Default: Story = {
  args: {
    ...mockNavigationProps,
  },
}
