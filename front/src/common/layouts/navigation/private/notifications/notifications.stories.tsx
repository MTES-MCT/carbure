import type { Meta, StoryObj } from "@storybook/react"
import { Notifications } from "./notifications"
import { userEvent, waitFor, within } from "@storybook/test"
import { okNotifications, okNotificationsAcked } from "./__test__/api"
import { COMMON_MOCKS } from "@storybook/mocks/common"

const meta: Meta<typeof Notifications> = {
  component: Notifications,
  title: "common/layouts/navigation/private/notifications",
  parameters: {
    mockingDate: new Date(2024, 3, 1),
    msw: {
      handlers: [...COMMON_MOCKS, okNotifications, okNotificationsAcked],
    },
  },
}

type Story = StoryObj<typeof Notifications>

export default meta

export const FirstTimeNotifications: Story = {
  parameters: {
    docs: {
      description: "First display when notifications are not acked",
    },
  },
  play: async ({ canvasElement }) => {
    const { getByRole } = within(canvasElement)
    const button = await waitFor(() =>
      getByRole("button", { name: "Notifications" })
    )

    await userEvent.click(button)
  },
}

export const SecondTimeNotifications: Story = {
  ...FirstTimeNotifications,
  parameters: {
    docs: {
      description: "Second display when notifications are acked",
    },
  },
  play: async (props) => {
    // Open the dropdown
    await FirstTimeNotifications.play?.(props)

    // All the notifications are acked automatically, close the dropdown by clicking outside
    await userEvent.click(document.body)

    // Reopen the dropdown
    await FirstTimeNotifications.play?.(props)
  },
}
