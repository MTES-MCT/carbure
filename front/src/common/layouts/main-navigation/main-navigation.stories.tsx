import type { Meta, StoryObj } from "@storybook/react"

import { MainNavigation } from "./main-navigation"
import {
  MainNavigationProvider,
  useMainNavigation,
} from "./main-navigation.context"
import { okUnauthorizedUser } from "carbure/__test__/api"
import { reactRouterParameters } from "storybook-addon-remix-react-router"

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
  parameters: {
    reactRouter: reactRouterParameters({
      location: {
        pathParams: { entityId: "3", year: "2024" },
      },
      routing: {
        path: "/org/:entityId/transactions/:year/drafts",
        handle: "Profile",
      },
    }),
  },
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
}

export const PublicLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [okUnauthorizedUser],
    },
  },
}
