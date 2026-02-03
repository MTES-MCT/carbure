import type { Meta, StoryObj } from "@storybook/react"
import { AnnualDeclarationStatusBadge } from "./annual-declaration-status-badge"
import { AnnualDeclarationStatus } from "biomethane/types"

const meta: Meta<typeof AnnualDeclarationStatusBadge> = {
  component: AnnualDeclarationStatusBadge,
  title: "modules/biomethane/components/AnnualDeclarationStatusBadge",
}

export default meta
type Story = StoryObj<typeof AnnualDeclarationStatusBadge>

export const AllStatuses: Story = {
  render: () => (
    <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
      <AnnualDeclarationStatusBadge
        status={AnnualDeclarationStatus.IN_PROGRESS}
      />
      <AnnualDeclarationStatusBadge status={AnnualDeclarationStatus.DECLARED} />
      <AnnualDeclarationStatusBadge status={AnnualDeclarationStatus.OVERDUE} />
    </div>
  ),
}
