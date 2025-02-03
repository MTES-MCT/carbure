import { useTranslation } from "react-i18next"
import { OperationsStatus } from "../types"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { formatOperationStatus } from "../operations.utils"

export const OperationBadge = ({ status }: { status?: OperationsStatus }) => {
  const { t } = useTranslation()
  const labelMapping: Record<OperationsStatus, BadgeProps["severity"]> = {
    [OperationsStatus.ACCEPTED]: "success",
    [OperationsStatus.CANCELED]: "error",
    [OperationsStatus.PENDING]: "warning",
    [OperationsStatus.REJECTED]: "error",
  }

  if (!status) return null

  return (
    <Badge severity={labelMapping[status]} noIcon>
      {t(formatOperationStatus(status))}
    </Badge>
  )
}
