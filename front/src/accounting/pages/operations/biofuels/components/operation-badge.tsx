import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { formatOperationStatus } from "accounting/utils/formatters"
import { OperationsStatus } from "accounting/types"

export const OperationBadge = ({ status }: { status?: OperationsStatus }) => {
  const labelMapping: Record<OperationsStatus, BadgeProps["severity"]> = {
    [OperationsStatus.ACCEPTED]: "success",
    [OperationsStatus.CANCELED]: "error",
    [OperationsStatus.PENDING]: "warning",
    [OperationsStatus.REJECTED]: "error",
    [OperationsStatus.DECLARED]: "success",
    [OperationsStatus.CORRECTED]: "success",
    [OperationsStatus.VALIDATED]: "success",
  }

  if (!status) return null

  return (
    <Badge severity={labelMapping[status]} noIcon>
      {formatOperationStatus(status)}
    </Badge>
  )
}
