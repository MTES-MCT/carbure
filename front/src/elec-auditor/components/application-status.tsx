import Tag, { TagVariant } from "common/components/tag"
import { ElecAuditorApplicationsStatus } from "elec-auditor/types"
import { useTranslation } from "react-i18next"

const statusToVariant: Record<ElecAuditorApplicationsStatus, TagVariant> = {
  [ElecAuditorApplicationsStatus.AuditInProgress]: "info",
  [ElecAuditorApplicationsStatus.AuditDone]: "success",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status?: ElecAuditorApplicationsStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecAuditorApplicationsStatus.AuditInProgress]: t("En attente"),
    [ElecAuditorApplicationsStatus.AuditDone]: t("Terminé"),
  }

  return (
    <Tag big={big} variant={!status ? "none" : statusToVariant[status]}>
      {!status ? "..." : statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
