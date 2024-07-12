import Tag, { TagVariant } from "common/components/tag"
import { ElecAuditStatus } from "elec-audit/types"
import { useTranslation } from "react-i18next"

const statusToVariant: Record<ElecAuditStatus, TagVariant> = {
  [ElecAuditStatus.AuditInProgress]: "info",
  [ElecAuditStatus.AuditDone]: "success",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status?: ElecAuditStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecAuditStatus.AuditInProgress]: t("En attente"),
    [ElecAuditStatus.AuditDone]: t("Terminé"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
