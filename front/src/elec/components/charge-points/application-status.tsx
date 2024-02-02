import { useTranslation } from "react-i18next"
import Tag, { TagVariant } from "common/components/tag"
import { ElecChargePointsApplicationStatus } from "elec/types"

const statusToVariant: Record<ElecChargePointsApplicationStatus, TagVariant> = {
  [ElecChargePointsApplicationStatus.Accepted]: "success",
  [ElecChargePointsApplicationStatus.Pending]: "info",
  [ElecChargePointsApplicationStatus.Rejected]: "danger",
  [ElecChargePointsApplicationStatus.AuditInProgress]: "warning",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status?: ElecChargePointsApplicationStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecChargePointsApplicationStatus.Pending]: t("En attente"),
    [ElecChargePointsApplicationStatus.Accepted]: t("Accepté"),
    [ElecChargePointsApplicationStatus.Rejected]: t("Refusé"),
    [ElecChargePointsApplicationStatus.AuditInProgress]: t("En cours d'audit"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
