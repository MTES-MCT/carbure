import { useTranslation } from "react-i18next"
import { DoubleCountingStatus as DCStatus } from "../types"
import Tag, { TagVariant } from "common/components/tag"

const statusToVariant: Record<DCStatus, TagVariant> = {
  [DCStatus.Accepted]: "success",
  [DCStatus.InProgress]: "info",
  [DCStatus.Pending]: "info",
  [DCStatus.Rejected]: "danger",
  [DCStatus.Lapsed]: "warning",
}

const DoubleCountingStatus = ({
  big,
  status,
}: {
  big?: boolean
  status: DCStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [DCStatus.Pending]: t("En attente"),
    [DCStatus.InProgress]: t("En attente"),
    [DCStatus.Accepted]: t("Accepté"),
    [DCStatus.Rejected]: t("Refusé"),
    [DCStatus.Lapsed]: t("Expiré"),
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default DoubleCountingStatus
