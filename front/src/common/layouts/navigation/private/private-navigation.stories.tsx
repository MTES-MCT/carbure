import type { Meta, StoryObj } from "@storybook/react"

import { PrivateNavigation } from "./private-navigation"
import {
  PrivateNavigationProvider,
  usePrivateNavigation,
} from "./private-navigation.context"
import { okUnauthorizedUser } from "carbure/__test__/api"
import { EntityType } from "carbure/types"
import { mockUser } from "carbure/__test__/helpers"

const meta: Meta<typeof PrivateNavigation> = {
  component: PrivateNavigation,
  decorators: [
    (Story) => (
      <PrivateNavigationProvider>
        <Story />
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
        <div style={{ background: "red", height: "200px" }}>
          this is the content of my page
        </div>
        <div style={{ background: "blue", height: "500px" }}>other content</div>
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
            },
          },
        }),
      ],
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
