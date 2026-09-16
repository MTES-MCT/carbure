import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"

import { ActionStatus } from "traceability/types"
import { getActionStatusLabel } from "traceability/utils/formatters"

const severityMapping: Record<ActionStatus, BadgeProps["severity"]> = {
  [ActionStatus.CREATED]: "info",
  [ActionStatus.PENDING]: "info",
  [ActionStatus.ACCEPTED]: "success",
  [ActionStatus.REJECTED]: "error",
  [ActionStatus.BLOCKED]: "error",
  [ActionStatus.DELETED]: "error",
}

export const ActionStatusBadge = ({
  status,
}: {
  status?: ActionStatus | null
}) => {
  if (!status) return null

  return (
    <Badge severity={severityMapping[status]}>
      {getActionStatusLabel(status)}
    </Badge>
  )
}
