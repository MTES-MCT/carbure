import type { Meta, StoryObj } from "@storybook/react"

import { PrivateNavigation } from "./private-navigation"
import {
  PrivateNavigationProvider,
  usePrivateNavigation,
} from "./private-navigation.context"
import { EntityType } from "carbure/types"
import { mockUser } from "carbure/__test__/helpers"
import { reactRouterParameters } from "storybook-addon-remix-react-router"

const meta: Meta<typeof PrivateNavigation> = {
  component: PrivateNavigation,
  title: "common/layouts/navigation/private",
  decorators: [
    (Story) => (
      <PrivateNavigationProvider>
        <div
          style={{ height: "100vh", display: "flex", flexDirection: "column" }}
        >
          <Story />
        </div>
      </PrivateNavigationProvider>
    ),
  ],
  parameters: {
    layout: "fullscreen",
  },
}
type Story = StoryObj<typeof PrivateNavigation>

export default meta

export const PrivateLayout: Story = {
  decorators: [
    (Story) => {
      usePrivateNavigation("this is a title")

      return <Story />
    },
  ],
  args: {
    children: (
      <>
        <div style={{ background: "#aba6a6", height: "200px" }}>
          this is the content of my page
        </div>
        <div style={{ background: "#eda7a7", height: "500px" }}>
          other content
        </div>
      </>
    ),
  },
  // parameters: {
  //   reactRouter: reactRouterParameters({
  //     location: {
  //       pathParams: { entityId: "3", year: "2024" },
  //     },
  //     routing: {
  //       path: "/org/:entityId/transactions/:year/in",
  //       handle: "Profile",
  //     },
  //   }),
  // },
}

export const OperatorLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [
        mockUser(EntityType.Operator, {
          right: {
            entity: {
              has_elec: true,
              has_saf: true,
              has_stocks: true,
            },
          },
        }),
      ],
    },
  },
}

export const AuditorLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.Auditor)],
    },
  },
}

export const ProducerLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.Producer)],
    },
  },
}

export const PowerOrHeatProducerLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.PowerOrHeatProducer)],
    },
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { entityId: "7", year: "2024" },
      },
      routing: {
        path: "/org/:entityId/transactions/:year/drafts",
        handle: "Profile",
      },
    }),
  },
}

export const TraderLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.Trader)],
    },
  },
}

export const AirlineLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.Airline)],
    },
  },
}

export const ChargePointOperatorLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.CPO)],
    },
  },
}
