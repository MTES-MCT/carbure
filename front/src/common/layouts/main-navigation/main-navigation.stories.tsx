import type { Meta, StoryObj } from "@storybook/react"

import { MainNavigation } from "./main-navigation"
import {
  MainNavigationProvider,
  useMainNavigation,
} from "./main-navigation.context"
import { okUnauthorizedUser } from "carbure/__test__/api"
import { reactRouterParameters } from "storybook-addon-remix-react-router"
import { EntityType } from "carbure/types"
import { mockUser } from "carbure/__test__/helpers"

const meta: Meta<typeof MainNavigation> = {
  component: MainNavigation,
  decorators: [
    (Story) => (
      <MainNavigationProvider>
        <Story />
      </MainNavigationProvider>
    ),
  ],
  parameters: {
    layout: "fullscreen",
  },
}
type Story = StoryObj<typeof MainNavigation>

export default meta

export const PrivateLayout: Story = {
  decorators: [
    (Story) => {
      useMainNavigation("this is a title")

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

export const PublicLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [okUnauthorizedUser],
    },
  },
}
