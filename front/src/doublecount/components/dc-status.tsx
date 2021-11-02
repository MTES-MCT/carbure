import { useTranslation } from "react-i18next"
import { DoubleCountingStatus as DCStatus } from "../types"
import Badge, { Variant } from "common/components/badge"

const statusToVariant: Record<DCStatus, Variant> = {
  [DCStatus.Accepted]: "success",
  [DCStatus.InProgress]: "warning",
  [DCStatus.Pending]: "info",
  [DCStatus.Rejected]: "danger",
  [DCStatus.Lapsed]: "warning",
}

const DoubleCountingStatus = ({ status }: { status: DCStatus }) => {
  const { t } = useTranslation()

  const statusLabels = {
    [DCStatus.Pending]: t("En attente"),
    [DCStatus.InProgress]: t("En cours"),
    [DCStatus.Accepted]: t("Accepté"),
    [DCStatus.Rejected]: t("Refusé"),
    [DCStatus.Lapsed]: t("Expiré"),
  }

  return (
    <Badge style={{ marginRight: 12 }} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Badge>
  )
}

export default DoubleCountingStatus
