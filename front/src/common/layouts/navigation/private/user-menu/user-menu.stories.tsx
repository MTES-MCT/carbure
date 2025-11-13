import type { Meta, StoryObj } from "@storybook/react"
import { UserMenu } from "./user-menu"
import { userEvent, waitFor, within } from "@storybook/test"

const meta: Meta<typeof UserMenu> = {
  component: UserMenu,
  title: "common/layouts/navigation/private/UserMenu",
}

type Story = StoryObj<typeof UserMenu>

export default meta

export const UserMenuOpened: Story = {
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const button = await waitFor(() => getByRole("button"))
    await userEvent.click(button)
  },
}
