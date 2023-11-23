import { useTranslation } from "react-i18next"
import { DoubleCountingStatus as DCStatus } from "../../types"
import Tag, { TagVariant } from "common/components/tag"

const statusToVariant: Record<DCStatus, TagVariant> = {
  [DCStatus.Accepted]: "success",
  [DCStatus.InProgress]: "info",
  [DCStatus.Pending]: "info",
  [DCStatus.Rejected]: "danger",
  [DCStatus.Lapsed]: "warning",
}

const ApplicationStatus = ({
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
    [DCStatus.Accepted]: t("Acceptée"),
    [DCStatus.Rejected]: t("Refusée"),
    [DCStatus.Lapsed]: t("Expirée"),
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
