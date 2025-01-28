import { useTranslation } from "react-i18next"
import { OperationsStatus } from "../types"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"

export const OperationBadge = ({ status }: { status?: OperationsStatus }) => {
  const { t } = useTranslation()
  const labelMapping: Record<
    OperationsStatus,
    { label: string; severity: BadgeProps["severity"] }
  > = {
    [OperationsStatus.ACCEPTED]: {
      label: t("Validé"),
      severity: "success",
    },
    [OperationsStatus.CANCELED]: {
      label: t("Annulé"),
      severity: "error",
    },
    [OperationsStatus.PENDING]: {
      label: t("En attente"),
      severity: "warning",
    },
    [OperationsStatus.REJECTED]: {
      label: t("Rejeté"),
      severity: "error",
    },
  }
  return (
    <Badge severity={status ? labelMapping[status].severity : "info"} noIcon>
      {status ? labelMapping[status].label : t("En attente")}
    </Badge>
  )
}
