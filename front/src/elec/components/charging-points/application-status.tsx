import { useTranslation } from "react-i18next"
import Tag, { TagVariant } from "common/components/tag"
import { ElecChargingPointsApplicationStatus } from "elec/types"

const statusToVariant: Record<ElecChargingPointsApplicationStatus, TagVariant> = {
  [ElecChargingPointsApplicationStatus.Accepted]: "success",
  [ElecChargingPointsApplicationStatus.Pending]: "info",
  [ElecChargingPointsApplicationStatus.Rejected]: "danger",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status: ElecChargingPointsApplicationStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecChargingPointsApplicationStatus.Pending]: t("En attente"),
    [ElecChargingPointsApplicationStatus.Accepted]: t("Accepté"),
    [ElecChargingPointsApplicationStatus.Rejected]: t("Refusé"),
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
