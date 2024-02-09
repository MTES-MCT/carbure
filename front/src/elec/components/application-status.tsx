import Tag, { TagVariant } from "common/components/tag"
import { ElecAuditApplicationStatus } from "elec/types"
import { useTranslation } from "react-i18next"

const statusToVariant: Record<ElecAuditApplicationStatus, TagVariant> = {
  [ElecAuditApplicationStatus.Accepted]: "success",
  [ElecAuditApplicationStatus.Pending]: "info",
  [ElecAuditApplicationStatus.Rejected]: "danger",
  [ElecAuditApplicationStatus.AuditInProgress]: "warning",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status?: ElecAuditApplicationStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecAuditApplicationStatus.Pending]: t("En attente"),
    [ElecAuditApplicationStatus.Accepted]: t("Accepté"),
    [ElecAuditApplicationStatus.Rejected]: t("Refusé"),
    [ElecAuditApplicationStatus.AuditInProgress]: t("En cours d'audit"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
