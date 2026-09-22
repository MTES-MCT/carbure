import type { Meta, StoryObj } from "@storybook/react"

import { ActionStatus } from "traceability/types"

import { ActionStatusBadge } from "./action-status-badge"

const meta: Meta<typeof ActionStatusBadge> = {
  component: ActionStatusBadge,
  title: "modules/traceability/components/ActionStatusBadge",
}

export default meta
type Story = StoryObj<typeof ActionStatusBadge>

export const AllStatuses: Story = {
  render: () => (
    <div
      style={{
        display: "flex",
        gap: "1rem",
        alignItems: "center",
        flexWrap: "wrap",
      }}
    >
      <ActionStatusBadge status={ActionStatus.CREATED} />
      <ActionStatusBadge status={ActionStatus.PENDING} />
      <ActionStatusBadge status={ActionStatus.ACCEPTED} />
      <ActionStatusBadge status={ActionStatus.REJECTED} />
      <ActionStatusBadge status={ActionStatus.BLOCKED} />
      <ActionStatusBadge status={ActionStatus.DELETED} />
    </div>
  ),
}
