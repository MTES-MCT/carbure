import type { Meta, StoryObj } from "@storybook/react"

import { MainNavigation } from "./main-navigation"
import {
  MainNavigationProvider,
  useMainNavigation,
} from "./main-navigation.context"

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

export const BaseLayout: Story = {
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
}
