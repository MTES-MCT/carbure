import type { Meta, StoryObj } from "@storybook/react"

import { NavigationLayout } from "./navigation-layout"

import { okUnauthorizedUser } from "carbure/__test__/api"
import { EntityType } from "carbure/types"
import { mockUser } from "carbure/__test__/helpers"
import {
  PrivateNavigationProvider,
  usePrivateNavigation,
} from "./private/private-navigation.context"

const meta: Meta<typeof NavigationLayout> = {
  component: NavigationLayout,
  title: "common/layouts/navigation",
  parameters: {
    layout: "fullscreen",
  },
}
type Story = StoryObj<typeof NavigationLayout>

export default meta

export const PrivateLayout: Story = {
  parameters: {
    msw: {
      handlers: [mockUser(EntityType.Producer)],
    },
  },
  decorators: [
    (Story) => {
      usePrivateNavigation("this is a title")

      return <Story />
    },
    (Story) => (
      <PrivateNavigationProvider>
        <Story />
      </PrivateNavigationProvider>
    ),
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
}

export const PublicLayout: Story = {
  ...PrivateLayout,
  parameters: {
    msw: {
      handlers: [okUnauthorizedUser],
    },
  },
}
