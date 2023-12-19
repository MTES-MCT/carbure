import { useTranslation } from "react-i18next"
import Tag, { TagVariant } from "common/components/tag"
import { ElecMeterReadingsApplicationStatus } from "elec/types"

const statusToVariant: Record<ElecMeterReadingsApplicationStatus, TagVariant> = {
  [ElecMeterReadingsApplicationStatus.Accepted]: "success",
  [ElecMeterReadingsApplicationStatus.Pending]: "info",
  [ElecMeterReadingsApplicationStatus.Rejected]: "danger",
}

const ApplicationStatus = ({
  big,
  status,
}: {
  big?: boolean
  status: ElecMeterReadingsApplicationStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecMeterReadingsApplicationStatus.Pending]: t("En attente"),
    [ElecMeterReadingsApplicationStatus.Accepted]: t("Accepté"),
    [ElecMeterReadingsApplicationStatus.Rejected]: t("Refusé"),
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
